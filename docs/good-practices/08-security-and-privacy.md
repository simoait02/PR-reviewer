---
title: Security and Privacy
description: Practices for secure defaults, authentication, authorization, input validation, secrets, threat modeling, privacy, vulnerability handling, and incident response.
category: security-and-privacy
audience: developers, security-engineers, architects, technical-leads
tags: authentication, authorization, secrets, privacy, threat-modeling, vulnerabilities
content_type: engineering-best-practice
---

# Security and Privacy

## Use secure defaults

Deny access by default, validate all untrusted input, encode output for its context, use parameterized queries, enforce least privilege, and fail safely. Treat every external input and dependency as untrusted.

## Protect secrets

Never commit passwords, tokens, private keys, or sensitive production configuration. Use a managed secret store, rotate credentials, restrict access, and prevent secrets from appearing in logs, traces, errors, or test fixtures.

## Control access

Authenticate identities and authorize every protected action on the server side. Separate duties, minimize service permissions, expire sessions and tokens appropriately, and audit sensitive actions.

## Protect data

Collect only necessary data. Classify it, encrypt it in transit and at rest where appropriate, define retention and deletion rules, and restrict access. Do not use real sensitive data in development without explicit approval and protection.

## Threat-model meaningful changes

Identify assets, trust boundaries, threats, abuse cases, mitigations, and residual risk for features handling identity, payments, personal data, files, privileged actions, or exposed interfaces.

## Prepare to respond

Maintain vulnerability reporting, patching, incident response, access revocation, evidence preservation, and notification procedures appropriate to the project.

## Apply threat modeling

For a feature, identify assets, actors, entry points, trust boundaries, privileged operations, and ways an attacker could alter, disclose, destroy, or deny access to resources. Consider spoofing, tampering, repudiation, information disclosure, denial of service, and privilege escalation. Record mitigations and residual risk; threat modeling is useful only when it changes design or controls.

## Secure authentication and sessions

Use established identity protocols and libraries rather than inventing cryptography or token formats. Protect credentials with appropriate hashing and rate limiting. Validate token issuer, audience, expiry, signature, and intended use. Revoke or rotate credentials after compromise. Avoid putting sensitive tokens in URLs, logs, browser storage, or error reports without a reasoned security design.

## Prevent common application flaws

Use parameterized database access, context-aware output encoding, safe file handling, allowlists for commands and redirects, CSRF protection where applicable, secure cookie settings, and strict content or transport policies where appropriate. Limit request size, upload type, archive expansion, recursion, and resource consumption to reduce denial-of-service risk.

## Build privacy in

Document the purpose and lawful basis for sensitive data where applicable. Minimize collection, separate identifiers from content when possible, restrict internal access, provide retention and deletion mechanisms, and ensure backups and logs follow the same policy. Avoid using production data for debugging or testing.

## Security checklist

- [ ] Threats and trust boundaries were considered.
- [ ] Authentication and authorization are server-side and deny by default.
- [ ] Inputs, uploads, redirects, and resource usage are constrained.
- [ ] Secrets are managed, rotated, and excluded from logs and source control.
- [ ] Dependencies and build artifacts are scanned appropriately.
- [ ] Sensitive data has classification, retention, deletion, and access rules.
- [ ] Security events are logged without exposing confidential data.
- [ ] Vulnerability response and incident escalation are defined.
