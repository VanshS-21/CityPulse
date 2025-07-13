# 🔐 CityPulse Credentials Management

This directory contains all credential management files and documentation for the CityPulse project.

## 📁 Files Overview

| File | Purpose | Security Level |
|------|---------|----------------|
| `citypulse-credentials.env` | Master credentials template | 🔒 **NEVER COMMIT** |
| `setup-credentials.js` | Interactive setup script | ✅ Safe to commit |
| `README.md` | This documentation | ✅ Safe to commit |

## 🚀 Quick Start

### 1. Initial Setup

```bash

# Navigate to credentials directory

cd credentials

# Run the interactive setup

node setup-credentials.js

# Follow the prompts to:

# - Setup Firebase credentials

# - Setup Google Cloud credentials  

# - Generate secure secrets

# - Copy to .env.local

```text
### 2. Manual Setup

```bash

# Copy the template

cp citypulse-credentials.env ../.env.local

# Edit with your actual values

nano ../.env.local
```text
## 🔥 Firebase Credentials Setup

### Required Firebase Configuration:

1. **Web App Config** (Public - frontend safe):
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY="your_api_key"
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN="citypulse-21.firebaseapp.com"
   NEXT_PUBLIC_FIREBASE_PROJECT_ID="citypulse-21"
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET="citypulse-21.appspot.com"
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID="123456789012"
   NEXT_PUBLIC_FIREBASE_APP_ID="1:123456789012:web:abcdef123456"
   ```

2. **Service Account** (Private - server-side only):
   ```env
   FIREBASE_SERVICE_ACCOUNT_KEY_PATH="./citypulse-21-8fd96b025d3c.json"
   ```

### How to Get Firebase Credentials:

#### Web App Configuration:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `citypulse-21`
3. Go to **Project Settings** > **General**
4. Scroll to **Your apps** section
5. Click on the web app or create one
6. Copy the config object values

#### Service Account Key:

1. Go to **Project Settings** > **Service Accounts**
2. Click **Generate new private key**
3. Download the JSON file
4. Place it in your project root as `citypulse-21-8fd96b025d3c.json`

## ☁️ Google Cloud Platform Setup

### Required GCP Configuration:

```env
GCP_PROJECT_ID="citypulse-21"
GOOGLE_CLOUD_REGION="us-central1"
GOOGLE_APPLICATION_CREDENTIALS="./citypulse-21-8fd96b025d3c.json"
```text
### Required APIs to Enable:

1. **Firebase Admin SDK API**
2. **Cloud Firestore API**
3. **BigQuery API**
4. **Pub/Sub API**
5. **Cloud Storage API**
6. **Identity and Access Management (IAM) API**

### How to Enable APIs:

```bash

# Using gcloud CLI

gcloud services enable firebase.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable iam.googleapis.com
```text
Or manually in [Google Cloud Console](https://console.cloud.google.com/apis/library).

## 🗺️ Google Maps Setup

### Required for Maps Functionality:

```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY="your_maps_api_key"
```text
### How to Get Maps API Key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Credentials**
3. Click **Create Credentials** > **API Key**
4. Restrict the key to specific APIs:
   - Maps JavaScript API
   - Geocoding API
   - Places API

## 🤖 AI Services Setup

### Google Gemini AI:

```env
GEMINI_API_KEY="your_gemini_api_key"
```text
### How to Get Gemini API Key:

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Create an API key
3. Copy the key to your credentials

## 📧 Email Services Setup

### SendGrid Configuration:

```env
SENDGRID_API_KEY="your_sendgrid_api_key"
SENDGRID_FROM_EMAIL="noreply@citypulse.com"
```text
### How to Setup SendGrid:

1. Create account at [SendGrid](https://sendgrid.com/)
2. Go to **Settings** > **API Keys**
3. Create a new API key with full access
4. Verify your sender email domain

## 🔐 Security Best Practices

### 1. Environment-Specific Credentials

```bash

# Development

.env.local

# Staging  

.env.staging

# Production

.env.production
```text
### 2. Never Commit Credentials

```gitignore

# Add to .gitignore

.env*
*credentials*
*.json
!credentials/README.md
!credentials/setup-credentials.js
```text
### 3. Rotate Credentials Regularly

- **API Keys**: Every 90 days
- **Service Account Keys**: Every 6 months
- **JWT Secrets**: Every 30 days

### 4. Use Least Privilege Access

- Grant minimum required permissions
- Use service accounts for server-side operations
- Restrict API keys to specific services

## 🚀 Deployment Configuration

### Vercel Deployment:

```bash

# Set environment variables

vercel env add NEXT_PUBLIC_FIREBASE_API_KEY
vercel env add FIREBASE_SERVICE_ACCOUNT_KEY

# ... add all required variables

```text
### Netlify Deployment:

```bash

# Set environment variables in Netlify dashboard

# Site Settings > Environment Variables

```text
### Docker Deployment:

```dockerfile

# Use environment variables

ENV NEXT_PUBLIC_FIREBASE_API_KEY=${NEXT_PUBLIC_FIREBASE_API_KEY}
ENV FIREBASE_SERVICE_ACCOUNT_KEY=${FIREBASE_SERVICE_ACCOUNT_KEY}
```text
## 🧪 Testing Credentials

### Validate Setup:

```bash

# Run validation script

node credentials/setup-credentials.js

# Choose option 2: Validate existing credentials

```text
### Test Firebase Connection:

```bash

# Test Firebase Admin SDK

npm run test:firebase
```text
### Test API Endpoints:

```bash

# Test authentication

curl -X GET http://localhost:3000/api/v1/auth

# Test with credentials

curl -X POST http://localhost:3000/api/v1/auth \
  -H "Content-Type: application/json" \
  -d '{"action":"register","email":"test@citypulse.com","password":"Password123!","name":"Test User"}'
```text
## 🆘 Troubleshooting

### Common Issues:

#### 1. Firebase Permission Denied

```bash
Error: Caller does not have required permission
```text
**Solution**: Add `Service Usage Consumer` role to service account

#### 2. Invalid Service Account Key

```bash
Error: Invalid JSON format
```text
**Solution**: Re-download service account key from Firebase Console

#### 3. API Key Restrictions

```bash
Error: This API key is not authorized
```text
**Solution**: Check API key restrictions in Google Cloud Console

#### 4. CORS Issues

```bash
Error: CORS policy blocked
```text
**Solution**: Add your domain to Firebase Auth authorized domains

### Getting Help:

1. Check the [Firebase Documentation](https://firebase.google.com/docs)
2. Review [Google Cloud Documentation](https://cloud.google.com/docs)
3. Check project issues on GitHub
4. Contact the development team

## 📋 Credentials Checklist

### ✅ Required for Basic Functionality:

- [ ] Firebase Web App Config
- [ ] Firebase Service Account Key
- [ ] GCP Project ID and Region
- [ ] JWT Secret
- [ ] App URL

### ✅ Required for Full Functionality:

- [ ] Google Maps API Key
- [ ] Gemini AI API Key
- [ ] SendGrid API Key
- [ ] Analytics Tracking IDs
- [ ] Social Media API Keys

### ✅ Required for Production:

- [ ] Production Firebase Project
- [ ] Production GCP Project
- [ ] SSL Certificates
- [ ] Domain Configuration
- [ ] Monitoring and Logging

## 🔄 Credential Rotation Schedule

| Credential Type | Rotation Frequency | Next Rotation |
|----------------|-------------------|---------------|
| JWT Secrets | Monthly | Set reminder |
| API Keys | Quarterly | Set reminder |
| Service Accounts | Bi-annually | Set reminder |
| OAuth Secrets | Annually | Set reminder |

---

#### 🔒 Remember: Security is everyone's responsibility. Keep credentials secure and never share them publicly!
