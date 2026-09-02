# Security Policy

## Responsible Disclosure

If you discover a security vulnerability in the Admin Control Plane project, please email:

**Support Contact**: Support@apexcapitalweb.com

Please include:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact assessment
- Your recommended fix (if available)

## Security Features

### 1. Hardware-Backed Authentication
- FIDO2/WebAuthn support with explicit AAGUID enforcement
- Whitelist-based hardware authenticator validation
- Rejection of deprecated formats (android-safetynet, none)

### 2. Immutable Audit Logging
- SHA-256 append-only audit chain
- All authentication events logged with cryptographic proofs
- Explicit "sandbox-mock" source labeling for controlled environments

### 3. Tier-0 Access Control
- Strict privilege separation
- Dual-control MFA gates for sensitive operations
- Hardware-backed keys required for all administrative access

### 4. Cloudflare Worker Isolation
- Separate admin-app directory excluded from public assets
- Use Cloudflare Access for identity-aware access control
- Do not rely solely on IP-based restrictions

## Compliance Standards

- **Readiness Date**: September 1, 2026
- **Environment Isolation**: Explicit sandbox-mock labeling
- **Audit Trail**: Immutable cryptographic logging
- **Key Material**: Secure generation with fallback strategies

## Security Considerations

### Do Not
- Store API keys or private keys in configuration files
- Use `CF-Connecting-IP` as sole proof of identity behind Cloudflare
- Deploy credentials to public static asset directories
- Mix live client trading systems with admin control plane

### Do
- Use Cloudflare Access or equivalent identity layer
- Implement Tailscale for private network control (additional layer)
- Maintain strict separation between admin and client-facing interfaces
- Log all administrative actions to immutable audit chain
- Regularly rotate hardware authenticator allowlists

## Incident Response

For security incidents:
1. Contact Support@apexcapitalweb.com immediately
2. Provide detailed timeline and system impact assessment
3. Preserve audit logs and evidence
4. Follow internal incident response procedures

## Version History

- **v1.0** (Sept 1, 2026): Initial hardened release
