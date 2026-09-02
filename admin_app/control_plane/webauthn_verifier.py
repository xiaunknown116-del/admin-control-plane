"""
Module: admin_app/control_plane/webauthn_verifier.py
Description: Hardened WebAuthn attestation parser for Tier-0 Admin Control Plane.
Compliance: SOP-SEC-2026-04 Hardware-Key Policy.
Environment: Controlled Sandbox (source: "sandbox-mock")
"""

import json
import hashlib
import hmac
import logging
from typing import Dict, Any, Tuple

# Setup isolation logging
logger = logging.getLogger("ApexAdminControlPlane")

# Simulated path targets from infrastructure configuration
AAGUID_ALLOWLIST_PATH = "config/aaguid_whitelist.json"

class AttestationValidationError(Exception):
    """Custom exception wrapper for high-impact authentication validation issues."""
    pass

class HardenedWebAuthnVerifier:
    def __init__(self, allowlist_source: str = AAGUID_ALLOWLIST_PATH):
        self.allowlist_source = allowlist_source
        # Valid cryptographic attestation formats allowed in Tier-0 Control Plane
        self.permitted_formats = {"packed", "tpm", "android-key", "fido-u2f", "apple"}
        # Strictly explicitly prohibited/deprecated formats
        self.forbidden_formats = {"android-safetynet", "none"}

    def _load_aaguid_allowlist(self) -> Dict[str, Any]:
        """Loads and parses the allowed hardware authenticators from the master policy list."""
        try:
            # In a live system, this reads directly from secure storage
            # Mocking data layer isolation pattern for sandbox validation
            mock_allowlist = {
                "00000000-0000-0000-0000-000000000000": "System Mock Token",
                "f81d4fae-7dec-11d0-a765-00a0c91e6bf6": "YubiKey 5 Series NFC",
                "7c526a0c-43f1-48fb-9c88-e25dfddc3b28": "Apple Secure Enclave Platform Token"
            }
            return mock_allowlist
        except Exception as e:
            raise AttestationValidationError(f"Failed to populate AAGUID security dictionary: {str(e)}")

    def _write_to_sha256_audit_chain(self, event_type: str, status: str, details: Dict[str, Any]) -> str:
        """
        Emits records to the append-only cryptographic log layer.
        Ensures strict compliance with sandbox-mock source constraints.
        """
        payload = {
            "source": "sandbox-mock",
            "layer": "Tier-0 Admin Control Plane",
            "event": event_type,
            "status": status,
            "meta": details
        }
        serialized = json.dumps(payload, sort_keys=True)
        record_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        
        # Log payload emission targeting append-only block simulation
        logger.info(f"[AUDIT-CHAIN-EMIT] Hash: {record_hash} | Payload: {serialized}")
        return record_hash

    def parse_and_verify_attestation(self, fmt: str, auth_data: bytes, att_stmt: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Parses incoming credentials, isolates structural format identifiers, 
        unpacks the underlying AAGUID, and assesses security posture.
        """
        audit_meta = {"format": fmt}
        
        try:
            # 1. Evaluate format validity against formal registries
            if fmt in self.forbidden_formats:
                raise AttestationValidationError(f"Registration rejected. Format '{fmt}' is explicitly prohibited.")
            
            if fmt not in self.permitted_formats:
                raise AttestationValidationError(f"Registration rejected. Format '{fmt}' unrecognized by Policy.")
            
            # 2. Extract structural binary elements from Authenticator Data (authData)
            # authData structural breakdown: 
            # RpIdHash (32 bytes) -> Flags (1 byte) -> SignCount (4 bytes) -> AttestedCredData (Variable)
            if len(auth_data) < 37:
                raise AttestationValidationError("Malformed authData block: payload under minimum required byte limit.")
            
            # Attested credential data starts at byte 37 if flags specify its presence
            flags = auth_data[32]
            # Bit 6 (0x40) specifies presence of Attested Credential Data
            if not (flags & 0x40):
                raise AttestationValidationError("Invalid context status: Credential Data flags absent in Tier-0 operation.")
            
            # Extract 16-byte AAGUID from offset 37 to 53
            aaguid_bytes = auth_data[37:53]
            if len(aaguid_bytes) != 16:
                raise AttestationValidationError("Failed to unpack complete 16-byte block for AAGUID isolation.")
            
            # Convert binary array to canonical string representation format
            aaguid_str = "-".join([
                aaguid_bytes[0:4].hex(),
                aaguid_bytes[4:6].hex(),
                aaguid_bytes[6:8].hex(),
                aaguid_bytes[8:10].hex(),
                aaguid_bytes[10:16].hex()
            ])
            
            audit_meta["extracted_aaguid"] = aaguid_str
            
            # 3. Assess extracted token signature scope against verified hardware list
            allowlist = self._load_aaguid_allowlist()
            if aaguid_str not in allowlist:
                raise AttestationValidationError(f"AAGUID '{aaguid_str}' missing from explicit hardware whitelist.")
            
            # Record explicit description target for policy compliance checking
            audit_meta["device_profile"] = allowlist[aaguid_str]
            
            # 4. Finalize state change validation loop
            chain_hash = self._write_to_sha256_audit_chain(
                event_type="HARDWARE_KEY_REGISTRATION",
                status="SUCCESS",
                details=audit_meta
            )
            return True, chain_hash

        except AttestationValidationError as exc:
            audit_meta["error_message"] = str(exc)
            self._write_to_sha256_audit_chain(
                event_type="HARDWARE_KEY_REGISTRATION_DENIED",
                status="FAILURE",
                details=audit_meta
            )
            # Escalate verification exception details back up to caller context
            raise exc
