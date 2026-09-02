# WebAuthn Attestation Format & AAGUID Verification Specification

**Document ID:** SPEC-SEC-2026-08  
**Scope:** Apex Capital Hardened Tier-0 Admin Control Plane  
**Status:** Approved  

---

## 1. Context & Purpose

Attestation proves that a credential was generated inside a genuine hardware security module or platform authenticator of an approved model. This specification defines how the Apex Capital Tier-0 Admin Control Plane validates WebAuthn `attestationObject` structures during administrative hardware key onboarding and step-up challenges.

---

## 2. Conveyance & Format Requirements

### Attestation Conveyance Preference
* **Operator / Viewer Roles:** `conveyance: "none"` or `"indirect"`.
* **Tier-0 Admin Registration:** `conveyance: "direct"` (or `"enterprise"` for corporate-managed endpoints).
* **Tier-0 Action Step-Up:** Assertion challenge (validates credential signature against previously registered public key).

### Supported Attestation Statement Formats (`fmt`)

| Format ID | Primary Devices | Validation Strategy | Status |
| :--- | :--- | :--- | :--- |
| `packed` | YubiKey, Titan Key, Nitrokey | Parse X.509 cert chain or self-signature, verify sig over `authenticatorData` + `clientDataHash`. | **Primary** |
| `tpm` | Windows Hello (TPM 2.0) | Verify AIK certificate chain, TPMv2 digest assertion, and quote signature. | **Supported** |
| `android-key` | Modern Android Platform Keys | Verify Key Attestation extension in certificate chain back to Google Root CA. | **Supported** |
| `apple` | Touch ID / Face ID / Secure Enclave | Verify X.509 certificate chain back to Apple WebAuthn Root CA. | **Supported** |
| `fido-u2f` | Legacy FIDO U2F Hardware Keys | Convert raw attestation signature to ECDSA P-256 signature and verify against U2F CA. | **Legacy** |
| `android-safetynet` | Older Android Devices | **Deprecated**. Requests using this format are rejected at API ingress. | **Prohibited** |

---

## 3. AAGUID Extraction & Allowlist Enforcement

Upon validating the attestation statement, the control plane parses the `authenticatorData` byte array to extract the **AAGUID** (Authenticator Attestation Global Unique Identifier) located at offset `37` (16 bytes).

### Verification Steps
1. Parse `attestationObject` using a CBOR decoder.
2. Verify `fmt` is in the allowed format set.
3. Validate signature over `authenticatorData || clientDataHash`.
4. Extract 128-bit `aaguid` from `authenticatorData[37..53]`.
5. Match `aaguid` against `config/aaguid_whitelist.json`.
6. Reject credential if AAGUID is absent or non-compliant.

---

## 4. Audit Chain Output

Every attestation evaluation generates an append-only audit event:

```json
{
  "event": "WEBAUTHN_ATTESTATION_EVALUATED",
  "timestamp": "2026-08-30T13:55:00Z",
  "actor": "secops-lead@apexcapital.internal",
  "fmt": "packed",
  "aaguid": "2fc0579f-6522-472c-8328-01f1d6450507",
  "status": "APPROVED",
  "source": "sandbox-mock",
  "sha256": "3a884812f862378f4a132bf5a92cf9c1efc0211333792f59266f8e7033503b44"
}
```

---

## 5. Policy Compliance

All Tier-0 administrative actions that involve credential step-up challenges must:
1. Request direct attestation conveyance.
2. Validate attestation format against the approved set.
3. Extract and verify AAGUID against the hardware allowlist.
4. Generate immutable audit log entries with SHA-256 hashes.
5. Reject any attestation using deprecated formats (e.g., `android-safetynet`).

For more details, see **SOP-SEC-2026-04: Hardware Key AAGUID Enforcement Policy**.
