# SOP-SEC-2026-04: Hardware Key AAGUID Enforcement Policy
# Classification: TIER-0 INTERNAL
# Effective Date: 2026-04-01

## 1. Objective
To restrict Tier-0 Admin Control Plane access to approved hardware authenticators via strict AAGUID (Authenticator Attestation GUID) allowing.

## 2. Policy Requirements
*   **All Admin Access**: Must use FIDO2/WebAuthn hardware tokens. Software authenticators are prohibited for Tier-0 operations unless using approved managed device enclaves (e.g., Corporate Managed Windows Hello TPM).
*   **AAGUID Enforcement**: The system must validate the AAGUID present in the attestation statement against the authoritative allowlist located at `config/aaguid_whitelist.json`.
*   **Prohibited Devices**: Generic U2F tokens or devices with unknown AAGUIDs (`00000000-0000-0000-0000-000000000000` except in Sandbox) are denied by default.

## 3. Approved Hardware List (Reference)
Refer to `config/aaguid_whitelist.json` for the active cryptographic allowlist.

## 4. Audit & Compliance
*   All registration attempts (Success/Failure) must be logged to the immutable SHA-256 audit chain.
*   Attestation format validation must occur *before* AAGUID checks.
