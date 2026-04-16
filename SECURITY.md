# Security Policy (Prototype Repo)

## Secret handling

- Never hardcode API keys, tokens, passwords, or private credentials in source files.
- Never commit raw credentials to git history.
- Pass secrets via environment variables or a local secret manager.
- Use redaction in logs, traces, and error messages.

## If a credential is exposed

1. Revoke/rotate the credential immediately at the provider.
2. Remove the credential from local files and command history where possible.
3. Replace with an environment variable reference.
4. If it was committed, rewrite history and rotate again.

## Environment variable convention

Use `.env.local` (gitignored) for local development:

```bash
JULES_API_KEY=...
```

Access at runtime through your process environment and validate presence at startup.

## Runtime policy alignment

This policy complements `IMPLEMENTATION_PLAN.md` security defaults:
- allowlisted network targets,
- no inline secrets in protocol files,
- redacted effect payloads in traces.
