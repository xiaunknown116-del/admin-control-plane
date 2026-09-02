# Apex Capital Web LLC — Operational Runbook

## Emergency Procedures & Incident Response

---

## 1. Service Health Monitoring

### Daily Health Checks
```bash
# Check worker status
curl -s https://apexcapitalweb.com/health | jq .

# Verify DNS propagation
dig apexcapitalweb.com @1.1.1.1

# Monitor Cloudflare Worker metrics
npx wrangler tail --env production
```

### Automated Monitoring
- Set up Cloudflare Analytics dashboard for traffic monitoring
- Configure uptime monitoring via statuspage.io or similar
- Enable Cloudflare firewall rate limiting (recommended: 100 req/min per IP)

---

## 2. Incident Response Procedures

### Authentication Service Degradation (502/503)
**Severity:** CRITICAL

**Steps:**
1. Check KV namespace status: `npx wrangler kv:namespace list`
2. Verify worker deployment: `npx wrangler deployments list`
3. Rollback to previous version: `git revert <commit-sha>`
4. Re-deploy: `git push origin main`
5. Notify security team via Slack

### Unauthorized Access Attempts (403 pattern)
**Severity:** HIGH

**Steps:**
1. Review audit logs: `curl -H "Authorization: Bearer $TOKEN" https://apexcapitalweb.com/api/audit/logs`
2. Identify attack source from CF logs
3. Add source IP to Cloudflare WAF blocklist
4. Escalate to security team
5. Post-incident review within 24 hours

### Suspected Data Breach
**Severity:** CRITICAL

**Steps:**
1. Immediately revoke all active session tokens: `wrangler kv:key delete "session:*" --binding ADMIN_KV`
2. Regenerate JWT_SIGNING_KEY: `wrangler secret put JWT_SIGNING_KEY`
3. Force re-authentication for all users
4. Notify leadership and legal team
5. Preserve all audit logs for forensics
6. File incident report with regulatory bodies if required

---

## 3. Deployment & Rollback

### Standard Deployment
```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes (test locally first)
npx wrangler dev

# 3. Commit and push
git add .
git commit -m "Feature: description"
git push origin feature/my-feature

# 4. Create pull request and get approval
# GitHub Actions automatically deploys to production on merge

# 5. Verify deployment
curl -I https://apexcapitalweb.com/health
```

### Emergency Rollback
```bash
# 1. Identify problematic commit
git log --oneline -10

# 2. Revert the commit
git revert <commit-sha>

# 3. Push to main (GitHub Actions auto-deploys)
git push origin main

# 4. Monitor health checks
npx wrangler tail --env production
```

---

## 4. Secrets Management

### Rotating JWT Signing Key
```bash
# Generate new 256-bit key
openssl rand -base64 32

# Update in Cloudflare
wrangler secret put JWT_SIGNING_KEY

# Note: All existing sessions will be invalidated
```

### Updating Webhook API Key
```bash
# Generate new API key
openssl rand -hex 32

# Update in Cloudflare
wrangler secret put WEBHOOKS_API_KEY

# Update webhook consumers with new key
```

---

## 5. KV Maintenance

### Cleanup Expired Data
```bash
# KV automatically purges expired keys based on TTL
# No manual intervention required

# To manually list all audit logs:
wrangler kv:key list --binding AUDIT_LEDGER_KV --preview false
```

### Backup Audit Logs
```bash
# Export audit logs to local file
wrangler kv:key list --binding AUDIT_LEDGER_KV --preview false > audit_backup.json

# Store securely (encrypted, off-site)
```

---

## 6. Escalation Contacts

**Level 1 - Operations Team**  
Email: support@apexcapitalweb.com  
Response Time: 1 hour  

**Level 2 - Security Team**  
Slack: #apex-security  
Response Time: 15 minutes  

**Level 3 - Executive Escalation**  
Email: security@apexcapitalweb.com (CTO)  
Response Time: 5 minutes  

---

**Last Updated:** September 2, 2026  
**Status:** ✅ APPROVED FOR PRODUCTION  
