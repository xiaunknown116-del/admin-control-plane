"""
Unit tests for HardenedWebAuthnVerifier.

The verifier is the policy gate for Tier-0 hardware-key registration:
attestation format allow/deny, authData structure, AAGUID whitelist, and
SHA-256 audit-chain emission. It previously had no automated coverage.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from admin_app.control_plane.webauthn_verifier import (  # noqa: E402
    AttestationValidationError,
    HardenedWebAuthnVerifier,
)

# AAGUIDs mirrored from the sandbox mock allowlist in the verifier.
YUBIKEY_AAGUID = bytes.fromhex("f81d4fae7dec11d0a76500a0c91e6bf6")
APPLE_AAGUID = bytes.fromhex("7c526a0c43f148fb9c88e25dfddc3b28")
MOCK_TOKEN_AAGUID = bytes(16)  # 00000000-0000-0000-0000-000000000000
# Present in AdminApp.jsx / docs, but not in the verifier mock allowlist.
UNLISTED_AAGUID = bytes.fromhex("2fc0579f6522472c832801f1d6450507")

YUBIKEY_AAGUID_STR = "f81d4fae-7dec-11d0-a765-00a0c91e6bf6"
APPLE_AAGUID_STR = "7c526a0c-43f1-48fb-9c88-e25dfddc3b28"
UNLISTED_AAGUID_STR = "2fc0579f-6522-472c-8328-01f1d6450507"


def build_auth_data(
    aaguid: bytes,
    *,
    flags: int = 0x40,
    sign_count: int = 1,
    extra: bytes = b"",
    truncate_to: int | None = None,
) -> bytes:
    """Minimal WebAuthn authenticatorData with optional attested credential data."""
    body = (b"\x11" * 32) + bytes([flags]) + sign_count.to_bytes(4, "big") + aaguid + extra
    if truncate_to is not None:
        return body[:truncate_to]
    return body


def expected_audit_hash(event_type: str, status: str, details: dict) -> str:
    payload = {
        "event": event_type,
        "layer": "Tier-0 Admin Control Plane",
        "meta": details,
        "source": "sandbox-mock",
        "status": status,
    }
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class TestParseAndVerifyAttestation(unittest.TestCase):
    def setUp(self) -> None:
        self.verifier = HardenedWebAuthnVerifier()

    def test_packed_yubikey_is_accepted_and_returns_deterministic_audit_hash(self) -> None:
        auth_data = build_auth_data(YUBIKEY_AAGUID)
        ok, chain_hash = self.verifier.parse_and_verify_attestation(
            "packed", auth_data, att_stmt={}
        )
        self.assertTrue(ok)
        expected = expected_audit_hash(
            "HARDWARE_KEY_REGISTRATION",
            "SUCCESS",
            {
                "format": "packed",
                "extracted_aaguid": YUBIKEY_AAGUID_STR,
                "device_profile": "YubiKey 5 Series NFC",
            },
        )
        self.assertEqual(chain_hash, expected)
        self.assertEqual(len(chain_hash), 64)

    def test_apple_secure_enclave_aaguid_is_accepted(self) -> None:
        ok, _ = self.verifier.parse_and_verify_attestation(
            "apple", build_auth_data(APPLE_AAGUID), {}
        )
        self.assertTrue(ok)

    def test_all_permitted_formats_are_accepted_for_allowlisted_aaguid(self) -> None:
        auth_data = build_auth_data(MOCK_TOKEN_AAGUID)
        for fmt in ("packed", "tpm", "android-key", "fido-u2f", "apple"):
            with self.subTest(fmt=fmt):
                ok, chain_hash = self.verifier.parse_and_verify_attestation(fmt, auth_data, {})
                self.assertTrue(ok)
                self.assertEqual(len(chain_hash), 64)

    def test_forbidden_formats_are_rejected_before_auth_data_is_parsed(self) -> None:
        for fmt in ("android-safetynet", "none"):
            with self.subTest(fmt=fmt):
                with self.assertRaises(AttestationValidationError) as ctx:
                    self.verifier.parse_and_verify_attestation(fmt, b"", {})
                self.assertIn("explicitly prohibited", str(ctx.exception))

    def test_unrecognized_format_is_rejected(self) -> None:
        with self.assertRaises(AttestationValidationError) as ctx:
            self.verifier.parse_and_verify_attestation("not-a-real-fmt", b"", {})
        self.assertIn("unrecognized by Policy", str(ctx.exception))

    def test_auth_data_shorter_than_37_bytes_is_malformed(self) -> None:
        with self.assertRaises(AttestationValidationError) as ctx:
            self.verifier.parse_and_verify_attestation("packed", b"\x00" * 36, {})
        self.assertIn("under minimum required byte limit", str(ctx.exception))

    def test_missing_attested_credential_data_flag_is_rejected(self) -> None:
        # Flags at offset 32 without bit 6 (0x40): user-present only.
        auth_data = build_auth_data(YUBIKEY_AAGUID, flags=0x01)
        with self.assertRaises(AttestationValidationError) as ctx:
            self.verifier.parse_and_verify_attestation("packed", auth_data, {})
        self.assertIn("Credential Data flags absent", str(ctx.exception))

    def test_truncated_aaguid_block_is_rejected(self) -> None:
        # 37-byte floor passes, but AAGUID slice is shorter than 16 bytes.
        truncated = build_auth_data(YUBIKEY_AAGUID, truncate_to=45)
        self.assertGreaterEqual(len(truncated), 37)
        self.assertLess(len(truncated), 53)
        with self.assertRaises(AttestationValidationError) as ctx:
            self.verifier.parse_and_verify_attestation("packed", truncated, {})
        self.assertIn("16-byte block", str(ctx.exception))

    def test_aaguid_absent_from_allowlist_is_rejected(self) -> None:
        auth_data = build_auth_data(UNLISTED_AAGUID)
        with self.assertRaises(AttestationValidationError) as ctx:
            self.verifier.parse_and_verify_attestation("packed", auth_data, {})
        self.assertIn(UNLISTED_AAGUID_STR, str(ctx.exception))
        self.assertIn("missing from explicit hardware whitelist", str(ctx.exception))

    def test_denial_emits_failure_audit_event_before_raising(self) -> None:
        with patch.object(
            self.verifier, "_write_to_sha256_audit_chain", wraps=self.verifier._write_to_sha256_audit_chain
        ) as emit:
            with self.assertRaises(AttestationValidationError):
                self.verifier.parse_and_verify_attestation("none", b"", {})
            emit.assert_called_once()
            kwargs = emit.call_args.kwargs
            self.assertEqual(kwargs["event_type"], "HARDWARE_KEY_REGISTRATION_DENIED")
            self.assertEqual(kwargs["status"], "FAILURE")
            self.assertEqual(kwargs["details"]["format"], "none")
            self.assertIn("error_message", kwargs["details"])

    def test_audit_payload_always_labels_sandbox_mock_source(self) -> None:
        recorded: list[str] = []

        original = self.verifier._write_to_sha256_audit_chain

        def capture(event_type, status, details):
            digest = original(event_type, status, details)
            recorded.append(digest)
            return digest

        with patch.object(self.verifier, "_write_to_sha256_audit_chain", side_effect=capture):
            self.verifier.parse_and_verify_attestation(
                "packed", build_auth_data(YUBIKEY_AAGUID), {}
            )
        self.assertEqual(len(recorded), 1)
        # Reconstruct the canonical payload the verifier hashes.
        details = {
            "format": "packed",
            "extracted_aaguid": YUBIKEY_AAGUID_STR,
            "device_profile": "YubiKey 5 Series NFC",
        }
        payload = {
            "event": "HARDWARE_KEY_REGISTRATION",
            "layer": "Tier-0 Admin Control Plane",
            "meta": details,
            "source": "sandbox-mock",
            "status": "SUCCESS",
        }
        self.assertEqual(
            recorded[0],
            hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
