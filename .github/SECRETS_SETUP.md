# GitHub Secrets Setup Guide

This guide explains the GitHub secrets configuration for CityPulse workflows.

## ✅ Current Status

**GitHub secrets are already configured for this repository!** The following secrets have been set up:

- ✅ `FIREBASE_API_KEY` - Firebase web app API key
- ✅ `FIREBASE_AUTH_DOMAIN` - Firebase auth domain
- ✅ `FIREBASE_PROJECT_ID` - Firebase project ID
- ✅ `FIREBASE_STORAGE_BUCKET` - Firebase storage bucket
- ✅ `FIREBASE_MESSAGING_SENDER_ID` - Firebase messaging sender ID
- ✅ `FIREBASE_APP_ID` - Firebase app ID
- ✅ `GCP_SA_KEY` - Google Cloud service account key
- ✅ `GCP_PROJECT_ID` - Google Cloud project ID
- ✅ `GCP_BUCKET` - Google Cloud storage bucket

## About VS Code Warnings

The "Context access might be invalid" warnings in VS Code should now be resolved since all required secrets are configured.

## Managing Secrets via GitHub CLI

If you need to update or add new secrets in the future:

```bash
# View current secrets
gh secret list

# Update an existing secret
gh secret set SECRET_NAME

# Set a secret from file
gh secret set SECRET_NAME < file.json

# Delete a secret
gh secret delete SECRET_NAME
```

## Optional Secrets for Enhanced Functionality

You may want to add these optional secrets for additional features:

### Vercel Secrets (for frontend deployment)

If you want to deploy to Vercel, add these from your [Vercel Dashboard](https://vercel.com/dashboard):

- `VERCEL_TOKEN` - Your Vercel deployment token
- `VERCEL_ORG_ID` - Your Vercel organization ID
- `VERCEL_PROJECT_ID` - Your Vercel project ID

### Security Scanning

- `SNYK_TOKEN` - Snyk security scanning token (for enhanced security checks)

## Verifying Current Setup

You can verify the current secrets configuration:

```bash
# List all configured secrets
gh secret list

# Check workflow status
gh workflow list
gh workflow view ci.yml
```

## Testing the Workflows

The workflows should now run without issues:

1. **CI Pipeline**: Automatically runs on push/PR with proper Firebase config
2. **Deploy Pipeline**: Can be triggered manually or on main branch push
3. **No more warnings**: VS Code warnings about "Context access might be invalid" should be resolved

## Security Best Practices

- ✅ Secrets are stored securely in GitHub (never in code)
- ✅ Different values used for development vs production
- 🔄 Regularly rotate your secrets (especially API keys)
- 🔒 Service accounts use principle of least privilege
- 📊 Monitor secret usage in workflow logs

## Quick Reference

For detailed GitHub CLI commands, see: `scripts/gh-secrets-quick-reference.md`
