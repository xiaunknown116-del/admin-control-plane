# Admin Control Plane

## Overview

A hardened, compliance-ready Admin Control Plane designed for secure infrastructure management with enterprise-grade authentication and cryptographic audit logging.

## Key Features

- **Dual-Control MFA Gates**: Hardware-backed WebAuthn (FIDO2) authentication with strict AAGUID enforcement
- **Immutable Cryptographic Audit Logs**: SHA-256 based append-only audit chain for all authentication events
- **Sandbox Isolation**: Explicit "sandbox-mock" source labeling for controlled testing environments
- **WebAuthn Hardening**: Support for multiple attestation formats (packed, TPM, Android-key, FIDO-U2F, Apple)
- **Hardware Whitelist Enforcement**: AAGUID-based device validation against approved hardware authenticators
- **Tier-0 Access Control**: Strict separation of privileges with compliance-ready governance

## Project Structure

```
admin-control-plane/
├── tools/
│   └── generate_test_keys.py          # Ed25519 keypair generator for sandbox testing
├── admin_app/
│   └── control_plane/
│       └── webauthn_verifier.py       # WebAuthn attestation parser and validator
├── config/
│   └── aaguid_whitelist.json          # Hardware authenticator allowlist
├── docs/
│   └── control-plane/
│       ├── webauthn-attestation-formats.md     # WebAuthn format specifications
│       └── SOP-SEC-2026-04_hardware-key-aaguid-policy.md  # AAGUID enforcement policy
└── README.md
```

## Compliance Status

**Readiness Date**: September 1, 2026

- ✅ Explicit sandbox-mock labeling for isolation
- ✅ Dual-control hardware MFA gates
- ✅ Immutable cryptographic audit logs (SHA-256)
- ✅ Strict separation from live client trading systems
- ✅ Clean multi-tab administrative interface

## Getting Started

### Prerequisites

- Python 3.8+
- PyNaCl (for production Ed25519 operations): `pip install pynacl`

### Generate Test Keys

```bash
python tools/generate_test_keys.py
```

Output:
```json
{
  "source": "sandbox-mock",
  "purpose": "Local Quorum Panel Testing Profile",
  "algorithm": "Ed25519",
  "keys": {
    "private_seed_hex": "...",
    "public_verify_key_hex": "..."
  }
}
```

### WebAuthn Verification

The `HardenedWebAuthnVerifier` class validates WebAuthn attestations:

```python
from admin_app.control_plane.webauthn_verifier import HardenedWebAuthnVerifier

verifier = HardenedWebAuthnVerifier()
success, chain_hash = verifier.parse_and_verify_attestation(
    fmt="packed",
    auth_data=b"...",
    att_stmt={}
)
```

## Policy Documents

- **SOP-SEC-2026-04**: Hardware Key AAGUID Enforcement Policy
- **WebAuthn Attestation Formats**: Complete format specifications and validation rules

## License

Apache License 2.0 — See LICENSE file for details.

## Security Contact

For security issues, please refer to the responsible disclosure policy in the SECURITY.md file.

## Support

Support Contact: Support@apexcapitalweb.com
