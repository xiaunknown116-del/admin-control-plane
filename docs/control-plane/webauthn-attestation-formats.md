# WebAuthn Attestation Format Enforcement
# Path: docs/control-plane/webauthn-attestation-formats.md
# Reference Policy: SOP-SEC-2026-04_hardware-key-aaguid-policy.md

This document establishes the official parsing guidelines for WebAuthn metadata inside the Apex Capital Hardened AdminApp environment. All credentials targeting the Tier-0 Admin Control Plane must adhere strictly to these profiles.

## Supported Formal Attestation Formats (IANA Registry)

| Format ID | Cryptographic Mechanics | Verification Requirements | Target Environment |
| :--- | :--- | :--- | :--- |
| **`packed`** | X.509 Certificate Chain or Self-Signed Signature (ECDSA / EdDSA) | Verify cert chain path against FIDO MDS metadata or structural self-signature. | **Mandatory** — Primary YubiKey, SoloKeys, and hardware security tokens. |
| **`tpm`** | AIK (Attestation Identity Key) certificate signed via trusted TPM 2.0 | Validate parsing of `certInfo` and `pubArea`. Ensure hash integrity against SHA-256 signatures. | **Corporate Endpoints** — Windows Hello for Business enterprise workstations. |
| **`android-key`** | X.509 Certificate Extension containing key description block | Verify `teeEnforced` parameters. Assert that key usage flags match device-bound configurations. | **Mobile Hardware** — TEE/StrongBox backed Android Enterprise devices. |
| **`fido-u2f`** | Legacy FIDO U2F X.509 attestation certificate format | Extract public keys from signature payloads; handle 65-byte uncompressed EC points. | **Legacy Tokens** — Backup/secondary physical tokens. |
| **`apple`** | X.509 leaf cert containing value matching SHA-256 hash of `authData` + `clientDataHash` | Verify certificate chain roots against known Apple WebAuthn Roots. | **macOS Workstations** — Enterprise Secure Enclave (Touch ID / Face ID). |

## Forbidden and Non-Attested Types

*   **`android-safetynet`**: **Explicitly Blocked**. Deprecated by Google. Any legacy fallback attempting this mechanism must be rejected with an immediate `SecurityAlert` payload.
*   **`none`**: Allowed **only** on consumer-facing dashboards or lower tier interfaces. Tier-0 Admin Control Plane enrollment attempts containing `fmt: "none"` must throw an uncatchable initialization error.

## Execution Constraints
1. **Direct Conveyance Requirement**: Relying Party configurations must request `attestation: "direct"`.
2. **AAGUID Extraction**: The 16-byte AAGUID must be unpacked directly from the `authData` payload prior to parsing.
3. **Allowlist Cross-Reference**: Match the parsed AAGUID explicitly against `config/aaguid_whitelist.json`.
