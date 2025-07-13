# GitHub CLI Secrets Quick Reference

## Prerequisites

```bash
# Install GitHub CLI (if not already installed)
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: See https://cli.github.com/

# Authenticate with GitHub
gh auth login
```

## Basic Secret Commands

```bash
# Set a secret (will prompt for value)
gh secret set SECRET_NAME

# Set a secret with value from stdin
echo "secret-value" | gh secret set SECRET_NAME

# Set a secret from file
gh secret set SECRET_NAME < path/to/file.txt

# List all secrets
gh secret list

# Delete a secret
gh secret delete SECRET_NAME
```

## CityPulse Specific Commands

### Required Firebase Secrets

```bash
gh secret set FIREBASE_API_KEY
gh secret set FIREBASE_AUTH_DOMAIN
gh secret set FIREBASE_PROJECT_ID
gh secret set FIREBASE_STORAGE_BUCKET
gh secret set FIREBASE_MESSAGING_SENDER_ID
gh secret set FIREBASE_APP_ID
```

### Optional Deployment Secrets

```bash
# Vercel (for frontend deployment)
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID

# Google Cloud (for backend deployment)
gh secret set GCP_SA_KEY < citypulse-21-8fd96b025d3c.json
gh secret set GCP_PROJECT_ID
gh secret set GCP_BUCKET

# Security scanning
gh secret set SNYK_TOKEN
```

## Useful Tips

### Set Multiple Secrets from Environment Variables

```bash
# If you have secrets in environment variables
gh secret set FIREBASE_API_KEY --body "$FIREBASE_API_KEY"
gh secret set FIREBASE_PROJECT_ID --body "$FIREBASE_PROJECT_ID"
```

### Set Secrets for Different Environments

```bash
# For organization secrets (if you have permissions)
gh secret set SECRET_NAME --org

# For specific repositories
gh secret set SECRET_NAME --repo owner/repo-name
```

### Verify Secrets

```bash
# List all secrets to verify they're set
gh secret list

# Check if a specific secret exists
gh secret list | grep SECRET_NAME
```

### Batch Operations

```bash
# Set multiple secrets from a file (one per line: NAME=value)
while IFS='=' read -r name value; do
  echo "$value" | gh secret set "$name"
done < secrets.txt
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Run `gh auth login` and follow the prompts
2. **Permission Denied**: Make sure you have admin access to the repository
3. **Secret Not Found**: Use `gh secret list` to verify the secret name

### Useful Commands

```bash
# Check authentication status
gh auth status

# View repository information
gh repo view

# Check workflow status
gh workflow list
gh workflow view deploy.yml
```

## Security Best Practices

- Never commit secrets to your repository
- Use different secrets for different environments
- Regularly rotate your secrets
- Use the principle of least privilege
- Monitor secret usage in workflow logs

## Getting Help

```bash
# Get help for secret commands
gh secret --help

# Get help for specific subcommands
gh secret set --help
gh secret list --help
```
