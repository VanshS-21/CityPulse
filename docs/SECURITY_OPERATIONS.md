# CityPulse Security Operations Guide

- \*Version\*\*: 0.1.0
- \*Last Updated\*\*: July 13, 2025
- \*Classification\*\*: Internal Use Only
- \*Target Audience\*\*: Security Engineers, DevOps, System Administrators

## Table of Contents

1.  [Security Overview](#security-overview)
1.  [Access Control Management](#access-control-management)
1.  [Security Monitoring](#security-monitoring)
1.  [Incident Response](#incident-response)
1.  [Vulnerability Management](#vulnerability-management)
1.  [Data Protection](#data-protection)

## Security Overview

### 🛡️ Security Architecture

````mermaid
graph TB
    subgraph "External"
        U[Users]
        A[Attackers]
    end

    subgraph "Security Perimeter"
        WAF[Web Application Firewall]
        LB[Load Balancer + SSL]
        CDN[CloudFlare CDN]
    end

    subgraph "Application Layer"
        FE[Frontend - Next.js]
        API[API Gateway]
        AUTH[Firebase Auth]
    end

    subgraph "Data Layer"
        FS[Firestore]
        BQ[BigQuery]
        CS[Cloud Storage]
    end

    subgraph "Infrastructure"
        GCP[Google Cloud Platform]
        IAM[Identity & Access Management]
        KMS[Key Management Service]
    end

    U --> CDN
    A -.-> WAF
    CDN --> WAF
    WAF --> LB
    LB --> FE
    FE --> AUTH
    FE --> API
    API --> FS
    API --> BQ
    API --> CS

    AUTH --> IAM
    FS --> KMS
    BQ --> KMS
    CS --> KMS
```text

### 🎯 Security Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| **Confidentiality**| 100% | Data encryption at rest and in transit |
|**Integrity**| 99.99% | Data validation and checksums |
|**Availability**| 99.9% | Uptime with DDoS protection |
|**Authentication**| 100% | Multi-factor authentication |
|**Authorization** | 100% | Role-based access control |

## Access Control Management

### 👤 Identity and Access Management (IAM)

#### User Role Matrix

```yaml

## IAM Role Definitions

roles:
  citizen:
    permissions:

      -   events:read
      -   events:create
      -   feedback:create
      -   profile:read
      -   profile:update

  authority:
    permissions:

      -   events:read
      -   events:update
      -   events:assign
      -   analytics:read
      -   users:read_limited

  admin:
    permissions:

      -   "*:*"  # Full access
    restrictions:

      -   require_mfa: true
      -   ip_whitelist: ["10.0.0.0/8", "192.168.1.0/24"]
      -   session_timeout: 3600  # 1 hour
```text

## Service Account Management

```bash

## !/bin/bash

## Service account creation and management

## Create service account for API

gcloud iam service-accounts create citypulse-api \

  -  -description="CityPulse API service account" \
  -  -display-name="CityPulse API"

## Grant minimal required permissions

gcloud projects add-iam-policy-binding citypulse-project \

  -  -member="serviceAccount:citypulse-api@citypulse-project.iam.gserviceaccount.com" \
  -  -role="roles/datastore.user"

gcloud projects add-iam-policy-binding citypulse-project \

  -  -member="serviceAccount:citypulse-api@citypulse-project.iam.gserviceaccount.com" \
  -  -role="roles/bigquery.dataEditor"

## Create and download key (store securely)

gcloud iam service-accounts keys create ./keys/citypulse-api-key.json \

  -  -iam-account=citypulse-api@citypulse-project.iam.gserviceaccount.com
```text

## Multi-Factor Authentication (MFA)

```javascript
// Implement MFA for admin users
import { getAuth, multiFactor, PhoneAuthProvider } from 'firebase/auth';

const enableMFA = async (user) => {
  const multiFactorSession = await multiFactor(user).getSession();

  const phoneAuthCredential = PhoneAuthProvider.credential(
    verificationId,
    verificationCode
  );

  const multiFactorAssertion = PhoneAuthProvider.assertion(phoneAuthCredential);

  await multiFactor(user).enroll(multiFactorAssertion, multiFactorSession);

  console.log('MFA enabled successfully');
};

// Enforce MFA for admin operations
const requireMFA = (requiredRole) => {
  return async (req, res, next) => {
    const user = req.user;

    if (user.roles.includes(requiredRole)) {
      const mfaFactors = multiFactor(user).enrolledFactors;

      if (mfaFactors.length === 0) {
        return res.status(403).json({
          error: 'MFA required for this operation'
        });
      }
    }

    next();
  };
};
```text

### 🔐 API Security

#### Rate Limiting and Throttling

```javascript
// Implement rate limiting
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = require('redis');

const redisClient = redis.createClient({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT
});

// Different limits for different endpoints
const apiLimiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl:api:'
  }),
  windowMs: 15 *60*1000, // 15 minutes
  max: 1000, // Limit each IP to 1000 requests per windowMs
  message: 'Too many requests from this IP',
  standardHeaders: true,
  legacyHeaders: false
});

const authLimiter = rateLimit({
  store: new RedisStore({
    client: redisClient,
    prefix: 'rl:auth:'
  }),
  windowMs: 15*60*1000,
  max: 5, // Limit auth attempts
  skipSuccessfulRequests: true
});

// Apply rate limiting
app.use('/api/', apiLimiter);
app.use('/auth/', authLimiter);
```text

#### Input Validation and Sanitization

```javascript
// Comprehensive input validation
const { body, param, query, validationResult } = require('express-validator');
const DOMPurify = require('isomorphic-dompurify');

// Event creation validation
const validateEventCreation = [
  body('title')
    .isLength({ min: 5, max: 200 })
    .trim()
    .escape()
    .withMessage('Title must be 5-200 characters'),

  body('description')
    .optional()
    .isLength({ max: 2000 })
    .customSanitizer(value => DOMPurify.sanitize(value))
    .withMessage('Description too long'),

  body('category')
    .isIn(['traffic', 'safety', 'civic', 'weather', 'social'])
    .withMessage('Invalid category'),

  body('location.lat')
    .isFloat({ min: -90, max: 90 })
    .withMessage('Invalid latitude'),

  body('location.lng')
    .isFloat({ min: -180, max: 180 })
    .withMessage('Invalid longitude'),

  // Custom validation for file uploads
  body('media')
    .optional()
    .custom((value, { req }) => {
      if (req.files && req.files.length > 5) {
        throw new Error('Maximum 5 files allowed');
      }
      return true;
    })
];

// Validation error handler
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors.array()
    });
  }
  next();
};

## ```text

## Security Monitoring

### 📊 Security Information and Event Management (SIEM)

#### Log Aggregation and Analysis

```yaml

## Fluentd configuration for security log collection

apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-security-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/citypulse/security.log
      pos_file /var/log/fluentd-security.log.pos
      tag citypulse.security
      format json
    </source>

    <filter citypulse.security>
      @type grep
      <regexp>
        key level
        pattern ^(WARN|ERROR|CRITICAL)$
      </regexp>
    </filter>

    <match citypulse.security>
      @type google_cloud_logging
      project_id citypulse-project
      zone us-central1-a
      vm_id citypulse-security
      vm_name citypulse-security-vm
    </match>

```text

## Intrusion Detection

```python

## Anomaly detection for security events

import pandas as pd
from sklearn.ensemble import IsolationForest
import logging

class SecurityAnomalyDetector:
    def**init**(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False

    def train(self, normal_traffic_data):
        """Train the model on normal traffic patterns"""
        features = self.extract_features(normal_traffic_data)
        self.model.fit(features)
        self.is_trained = True
        logging.info("Anomaly detection model trained")

    def detect_anomalies(self, current_traffic):
        """Detect anomalies in current traffic"""
        if not self.is_trained:
            raise ValueError("Model not trained")

        features = self.extract_features(current_traffic)
        anomaly_scores = self.model.decision_function(features)
        anomalies = self.model.predict(features)

## Flag anomalies (score = -1)

        anomalous_requests = current_traffic[anomalies == -1]

        if len(anomalous_requests) > 0:
            self.alert_security_team(anomalous_requests)

        return anomalous_requests

    def extract_features(self, traffic_data):
        """Extract features for anomaly detection"""
        return traffic_data[['request_rate',
            'response_time',
            'error_rate',
            'unique_ips',
            'payload_size',
            'geographic_diversity']]

    def alert_security_team(self, anomalies):
        """Send alerts for detected anomalies"""
        alert_data = {
            'timestamp': pd.Timestamp.now(),
            'anomaly_count': len(anomalies),
            'severity': 'HIGH' if len(anomalies) > 10 else 'MEDIUM',
            'details': anomalies.to_dict('records')
        }

## Send to monitoring system

        logging.critical(f"Security anomaly detected: {alert_data}")

```text

## Real-time Threat Detection

```javascript

// Real-time threat detection middleware
const geoip = require('geoip-lite');
const useragent = require('useragent');

const threatDetection = (req, res, next) => {
  const clientIP = req.ip;
  const userAgent = req.get('User-Agent');
  const geo = geoip.lookup(clientIP);
  const agent = useragent.parse(userAgent);

  // Threat indicators
  const threats = [];

  // Check for suspicious IP patterns
  if (isKnownMaliciousIP(clientIP)) {
    threats.push('MALICIOUS_IP');
  }

  // Check for bot patterns
  if (isSuspiciousUserAgent(userAgent)) {
    threats.push('SUSPICIOUS_BOT');
  }

  // Check for geographic anomalies
  if (geo && isUnusualGeography(geo.country)) {
    threats.push('GEOGRAPHIC_ANOMALY');
  }

  // Check request patterns
  if (isSuspiciousRequestPattern(req)) {
    threats.push('SUSPICIOUS_PATTERN');
  }

  // Log and potentially block
  if (threats.length > 0) {
    logSecurityEvent({
      type: 'THREAT_DETECTED',
      ip: clientIP,
      userAgent: userAgent,
      threats: threats,
      timestamp: new Date(),
      request: {
        method: req.method,
        url: req.url,
        headers: req.headers
      }
    });

    // Block high-risk requests
    if (threats.includes('MALICIOUS_IP')) {
      return res.status(403).json({
        error: 'Access denied'
      });
    }
  }

  next();
};

const isKnownMaliciousIP = (ip) => {
  // Check against threat intelligence feeds
  // Implementation would check against blacklists
  return false;
};

const isSuspiciousUserAgent = (userAgent) => {
  const suspiciousPatterns = [/sqlmap/i,
    /nikto/i,
    /nmap/i,
    /masscan/i,
    /python-requests/i];

  return suspiciousPatterns.some(pattern => pattern.test(userAgent));
};

## ```text 2

## Incident Response

### 🚨 Incident Response Plan

#### Incident Classification

```yaml

## Incident severity levels

severity_levels:
  P1_CRITICAL:
    description: "System completely unavailable or data breach"
    response_time: "15 minutes"
    escalation: "Immediate C-level notification"
    examples:

      -   "Complete system outage"
      -   "Data breach with PII exposure"
      -   "Successful unauthorized access"

  P2_HIGH:
    description: "Significant functionality impaired"
    response_time: "1 hour"
    escalation: "Security team lead notification"
    examples:

      -   "Authentication system down"
      -   "Suspected intrusion attempt"
      -   "DDoS attack in progress"

  P3_MEDIUM:
    description: "Minor functionality impaired"
    response_time: "4 hours"
    escalation: "On-call engineer notification"
    examples:

      -   "Elevated error rates"
      -   "Suspicious activity detected"
      -   "Non-critical service degradation"

  P4_LOW:
    description: "Minimal impact or informational"
    response_time: "24 hours"
    escalation: "Standard ticket queue"
    examples:

      -   "Security scan alerts"
      -   "Policy violations"
      -   "Routine security events"
```text

## Incident Response Workflow

```mermaid
flowchart TD
    A[Security Event Detected] --> B{Assess Severity}
    B -->|P1/P2| C[Immediate Response]
    B -->|P3/P4| D[Standard Response]

    C --> E[Activate Incident Team]
    E --> F[Contain Threat]
    F --> G[Investigate & Document]
    G --> H[Eradicate Threat]
    H --> I[Recover Systems]
    I --> J[Post-Incident Review]

    D --> K[Assign to Engineer]
    K --> L[Investigate]
    L --> M[Resolve & Document]
    M --> J

    J --> N[Update Procedures]
    N --> O[Close Incident]
```text

### Incident Response Playbooks

```bash

## !/bin/bash 2

## Security Incident Response Playbook

## P1 Critical Incident Response

respond_to_critical_incident() {
    echo "CRITICAL INCIDENT DETECTED - Initiating response"

## 1. Immediate containment

    echo "Step 1: Immediate containment"

## Isolate affected systems

    kubectl scale deployment citypulse-api --replicas=0

## Block suspicious IPs at firewall level

    gcloud compute firewall-rules create block-suspicious-ips \

        -  -action=DENY \
        -  -rules=tcp,udp \
        -  -source-ranges="$SUSPICIOUS_IP_LIST"

## 2. Notify incident team

    echo "Step 2: Notifying incident team"
    curl -X POST "$SLACK_WEBHOOK" \

        -  H 'Content-type: application/json' \
        -  -data '{"text":"🚨 CRITICAL SECURITY INCIDENT - All hands on deck!"}'

## 3. Preserve evidence

    echo "Step 3: Preserving evidence"

## Create snapshots of affected systems

    gcloud compute disks snapshot citypulse-api-disk \

        -  -snapshot-names="incident-$(date +%Y%m%d-%H%M%S)" \
        -  -zone=us-central1-a

## Export logs

    gcloud logging read "timestamp>=\"$(date -d '1 hour ago' --iso-8601)\"" \

        -  -format=json > "incident-logs-$(date +%Y%m%d-%H%M%S).json"

## 4. Begin investigation

    echo "Step 4: Beginning investigation"

## Analyze recent access logs

    grep -E "(FAILED|ERROR|UNAUTHORIZED)" /var/log/citypulse/access.log | tail -100

## Check for unusual network activity

    netstat -tuln | grep LISTEN

    echo "Critical incident response initiated. Continue with detailed investigation."
}

## Data Breach Response

respond_to_data_breach() {
    echo "DATA BREACH DETECTED - Initiating breach response"

## 1. Immediate containment 2

## Revoke all API keys

    python scripts/revoke_all_api_keys.py

## 2. Legal and compliance notification

## Notify legal team within 1 hour

    echo "Notifying legal team and preparing breach notifications"

## 3. User notification preparation

## Prepare user notification templates

    echo "Preparing user breach notifications"

## 4. Regulatory compliance

## GDPR requires notification within 72 hours

    echo "Initiating regulatory notification process"
}

## ```text 3

## Vulnerability Management

### 🔍 Vulnerability Scanning

#### Automated Security Scanning

```yaml

## GitHub Actions security scanning workflow

name: Security Scan
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:

    -   cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:

    -   uses: actions/checkout@v3

    -   name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    -   name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

    -   name: Run Snyk security scan
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high

    -   name: Run OWASP ZAP scan
      uses: zaproxy/action-full-scan@v0.4.0
      with:
        target: '[Your CityPulse URL]'
        rules_file_name: '.zap/rules.tsv'
        cmd_options: '-a'

```text

## Dependency Vulnerability Management

```javascript

// Automated dependency vulnerability checking
const { execSync } = require('child_process');
const fs = require('fs');

class VulnerabilityManager {
  constructor() {
    this.vulnerabilityThresholds = {
      critical: 0,  // No critical vulnerabilities allowed
      high: 2,      // Maximum 2 high severity
      medium: 10,   // Maximum 10 medium severity
      low: 50       // Maximum 50 low severity
    };
  }

  async scanDependencies() {
    console.log('Scanning dependencies for vulnerabilities...');

    try {
      // Run npm audit
      const auditResult = execSync('npm audit --json', { encoding: 'utf8' });
      const audit = JSON.parse(auditResult);

      // Run Snyk scan
      const snykResult = execSync('snyk test --json', { encoding: 'utf8' });
      const snyk = JSON.parse(snykResult);

      // Analyze results
      const vulnerabilities = this.analyzeVulnerabilities(audit, snyk);

      // Check against thresholds
      const exceedsThreshold = this.checkThresholds(vulnerabilities);

      if (exceedsThreshold) {
        throw new Error('Vulnerability threshold exceeded');
      }

      // Generate report
      this.generateVulnerabilityReport(vulnerabilities);

      return vulnerabilities;
    } catch (error) {
      console.error('Vulnerability scan failed:', error.message);
      throw error;
    }
  }

  analyzeVulnerabilities(audit, snyk) {
    const vulnerabilities = {
      critical: [],
      high: [],
      medium: [],
      low: []
    };

    // Process npm audit results
    if (audit.vulnerabilities) {
      Object.values(audit.vulnerabilities).forEach(vuln => {
        vulnerabilities[vuln.severity].push({
          source: 'npm',
          package: vuln.name,
          severity: vuln.severity,
          title: vuln.title,
          url: vuln.url
        });
      });
    }

    // Process Snyk results
    if (snyk.vulnerabilities) {
      snyk.vulnerabilities.forEach(vuln => {
        vulnerabilities[vuln.severity].push({
          source: 'snyk',
          package: vuln.packageName,
          severity: vuln.severity,
          title: vuln.title,
          url: vuln.url
        });
      });
    }

    return vulnerabilities;
  }

  checkThresholds(vulnerabilities) {
    for (const [severity, threshold] of Object.entries(this.vulnerabilityThresholds)) {
      if (vulnerabilities[severity].length > threshold) {
console.error(`${severity} vulnerability threshold exceeded: ${vulnerabilities[severity].length} > ${threshold}`);
        return true;
      }
    }
    return false;
  }

  generateVulnerabilityReport(vulnerabilities) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        critical: vulnerabilities.critical.length,
        high: vulnerabilities.high.length,
        medium: vulnerabilities.medium.length,
        low: vulnerabilities.low.length
      },
      details: vulnerabilities
    };

    fs.writeFileSync('./reports/vulnerability-report.json', JSON.stringify(report, null, 2));
    console.log('Vulnerability report generated: ./reports/vulnerability-report.json');
  }
}

```text

### 🔧 Patch Management

```bash

## !/bin/bash 3

## Automated patch management system

PATCH_LOG="/var/log/citypulse/patch-management.log"
MAINTENANCE_WINDOW="02:00-04:00"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$PATCH_LOG"
}

check_maintenance_window() {
    current_hour=$(date '+%H')
    if [[$current_hour -ge 2 && $current_hour -lt 4]]; then
        return 0  # In maintenance window
    else
        return 1  # Outside maintenance window
    fi
}

update_system_packages() {
    log_message "Starting system package updates"

## Update package lists

    apt-get update

## Get list of upgradeable packages

    upgradeable=$(apt list --upgradeable 2>/dev/null | grep -v "WARNING" | wc -l)

    if [[$upgradeable -gt 1]]; then
        log_message "Found $upgradeable packages to update"

## Apply security updates only

        unattended-upgrade --dry-run

        if check_maintenance_window; then
            log_message "Applying security updates during maintenance window"
            unattended-upgrade
        else
            log_message "Deferring updates until maintenance window"
        fi
    else
        log_message "No packages to update"
    fi
}

update_container_images() {
    log_message "Checking for container image updates"

## Get current image versions

    current_images=$(kubectl get deployments -o jsonpath='{.items[*].spec.template.spec.containers[*].image}')

## Check for updates (simplified - would integrate with registry API)

    for image in $current_images; do
        log_message "Checking updates for image: $image"

## Pull latest image info

        latest_digest=$(docker manifest inspect "$image:latest" | jq -r '.config.digest')
        current_digest=$(docker inspect "$image" | jq -r '.[0].RepoDigests[0]')

        if [["$latest_digest" != "$current_digest"]]; then
            log_message "Update available for $image"

            if check_maintenance_window; then
                log_message "Updating $image during maintenance window"
                kubectl set image deployment/citypulse-api api="$image:latest"
                kubectl rollout status deployment/citypulse-api
            fi
        fi
    done
}

## Main patch management routine

main() {
    log_message "Starting patch management cycle"

## Check for system updates

    update_system_packages

## Check for container updates

    update_container_images

## Verify system health after updates

    if systemctl is-active --quiet citypulse-api; then
        log_message "System health check passed"
    else
        log_message "ERROR: System health check failed"

## Trigger rollback procedures

        kubectl rollout undo deployment/citypulse-api
    fi

    log_message "Patch management cycle completed"
}

## Run if called directly

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

## ```text 4

## Data Protection

### 🔒 Encryption Management

#### Data Encryption at Rest

```python

## Data encryption utilities

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def **init**(self, password: str = None):
        if password:
            self.key = self._derive_key_from_password(password)
        else:
            self.key = self._load_or_generate_key()

        self.cipher_suite = Fernet(self.key)

    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password"""
        password_bytes = password.encode()
        salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key

    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate new one"""
        key_file = '/etc/citypulse/encryption.key'

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()

## Store key securely (in production, use KMS)

            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)

## Set secure permissions

            os.chmod(key_file, 0o600)

            return key

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()

## Usage in application

class SecureUserProfile:
    def **init**(self):
        self.encryption = DataEncryption()

    def store_sensitive_data(self, user_id: str, sensitive_data: dict):
        """Store sensitive user data with encryption"""
        encrypted_data = {}

        for key, value in sensitive_data.items():
            if key in ['email', 'phone', 'address']:
                encrypted_data[key] = self.encryption.encrypt_data(str(value))
            else:
                encrypted_data[key] = value

## Store in database

        return self._save_to_database(user_id, encrypted_data)

    def retrieve_sensitive_data(self, user_id: str) -> dict:
        """Retrieve and decrypt sensitive user data"""
        encrypted_data = self._load_from_database(user_id)
        decrypted_data = {}

        for key, value in encrypted_data.items():
            if key in ['email', 'phone', 'address']:
                decrypted_data[key] = self.encryption.decrypt_data(value)
            else:
                decrypted_data[key] = value

        return decrypted_data
```text

## Key Management with Google Cloud KMS

```python

## Google Cloud KMS integration

from google.cloud import kms
import base64

class CloudKMSManager:
    def **init**(self, project_id: str, location: str, key_ring: str, key_name: str):
        self.client = kms.KeyManagementServiceClient()
        self.key_name = self.client.crypto_key_path(
            project_id, location, key_ring, key_name
        )

    def encrypt_data(self, plaintext: str) -> str:
        """Encrypt data using Cloud KMS"""
        plaintext_bytes = plaintext.encode('utf-8')

        response = self.client.encrypt(
            request={'name': self.key_name, 'plaintext': plaintext_bytes}
        )

        return base64.b64encode(response.ciphertext).decode('utf-8')

    def decrypt_data(self, ciphertext: str) -> str:
        """Decrypt data using Cloud KMS"""
        ciphertext_bytes = base64.b64decode(ciphertext.encode('utf-8'))

        response = self.client.decrypt(
            request={'name': self.key_name, 'ciphertext': ciphertext_bytes}
        )

        return response.plaintext.decode('utf-8')

    def rotate_key(self):
        """Rotate encryption key"""
        parent = self.client.crypto_key_path(
            self.project_id, self.location, self.key_ring, self.key_name
        )

        response = self.client.create_crypto_key_version(
            request={'parent': parent, 'crypto_key_version': {}}
        )

        return response.name
```text

## 🛡️ Data Loss Prevention (DLP)

```python

## Data Loss Prevention implementation

import re
from typing import List, Dict, Any

class DLPScanner:
    def **init**(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }

    def scan_text(self, text: str) -> Dict[str, List[str]]:
        """Scan text for sensitive data patterns"""
        findings = {}

        for data_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[data_type] = matches

        return findings

    def sanitize_text(self, text: str) -> str:
        """Remove or mask sensitive data from text"""
        sanitized = text

        for data_type, pattern in self.patterns.items():
            if data_type == 'email':
                sanitized = re.sub(pattern, '[EMAIL_REDACTED]', sanitized)
            elif data_type == 'phone':
                sanitized = re.sub(pattern, '[PHONE_REDACTED]', sanitized)
            elif data_type == 'ssn':
                sanitized = re.sub(pattern, '[SSN_REDACTED]', sanitized)
            elif data_type == 'credit_card':
                sanitized = re.sub(pattern, '[CARD_REDACTED]', sanitized)

        return sanitized

    def validate_data_before_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize data before storage"""
        validated_data = {}

        for key, value in data.items():
            if isinstance(value, str):

## Scan for sensitive data

                findings = self.scan_text(value)

                if findings:

## Log potential data leak

                    self._log_dlp_finding(key, findings)

## Sanitize if necessary

                    if key not in ['email', 'phone']:  # These fields should contain this data
                        value = self.sanitize_text(value)

                validated_data[key] = value
            else:
                validated_data[key] = value

        return validated_data

    def _log_dlp_finding(self, field: str, findings: Dict[str, List[str]]):
        """Log DLP findings for security review"""
        import logging

        logger = logging.getLogger('dlp')
        logger.warning(f"Sensitive data detected in field '{field}': {findings}")

## ```text 5

-  This security operations guide provides comprehensive procedures for maintaining the security posture of the CityPulse
platform.*
````
