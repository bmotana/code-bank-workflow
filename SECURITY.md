# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Please report security issues responsibly. To report a security vulnerability:

1. Use GitHub's **Private Vulnerability Reporting** feature via the **Security** tab of the repository to submit an advisory.
2. Alternatively, reach out to the repository maintainers through GitHub private communications.

Please include:
- A description of the issue
- Steps to reproduce (if possible)
- Impact assessment

You should receive an acknowledgment within a few business days. Please give reasonable time to investigate and address the vulnerability before public disclosure.

## Secrets

Never commit API tokens, `.env` files, or private Notion database credentials. Use `.env.example` as the template for required variables.
