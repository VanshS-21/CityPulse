#!/usr/bin/env node

/**
 * CityPulse Credentials Setup Script
 * Helps set up and validate all project credentials
 */

const fs = require('fs')
const path = require('path')
const readline = require('readline')

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
})

class CredentialsManager {
  constructor() {
    this.credentialsPath = path.join(__dirname, 'citypulse-credentials.env')
    this.envPath = path.join(__dirname, '..', '.env')
    this.requiredCredentials = {
      firebase: [
        'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
        'NEXT_PUBLIC_FIREBASE_API_KEY',
        'FIREBASE_SERVICE_ACCOUNT_KEY_PATH',
      ],
      gcp: ['GCP_PROJECT_ID', 'GOOGLE_CLOUD_REGION'],
      api: ['JWT_SECRET', 'NEXT_PUBLIC_APP_URL'],
    }
  }

  async start() {
    console.log('🔥 CityPulse Credentials Setup')
    console.log('================================\n')

    const action = await this.askQuestion(
      'What would you like to do?\n' +
        '1. Setup new credentials\n' +
        '2. Validate existing credentials\n' +
        '3. Copy credentials to .env.local\n' +
        '4. Generate secure secrets\n' +
        'Enter choice (1-4): '
    )

    switch (action.trim()) {
      case '1':
        await this.setupCredentials()
        break
      case '2':
        await this.validateCredentials()
        break
      case '3':
        await this.copyToEnv()
        break
      case '4':
        await this.generateSecrets()
        break
      default:
        console.log('Invalid choice. Exiting...')
    }

    rl.close()
  }

  async setupCredentials() {
    console.log('\n🛠️  Setting up credentials...\n')

    if (!fs.existsSync(this.credentialsPath)) {
      console.log('❌ Credentials template not found!')
      console.log(
        'Please ensure citypulse-credentials.env exists in the credentials folder.'
      )
      return
    }

    const template = fs.readFileSync(this.credentialsPath, 'utf8')
    console.log('✅ Found credentials template')

    const setupFirebase = await this.askQuestion(
      'Setup Firebase credentials? (y/n): '
    )
    if (setupFirebase.toLowerCase() === 'y') {
      await this.setupFirebaseCredentials()
    }

    const setupGCP = await this.askQuestion(
      'Setup Google Cloud credentials? (y/n): '
    )
    if (setupGCP.toLowerCase() === 'y') {
      await this.setupGCPCredentials()
    }

    console.log('\n✅ Credentials setup completed!')
    console.log(
      '📝 Please review and update the credentials file with your actual values.'
    )
  }

  async setupFirebaseCredentials() {
    console.log('\n🔥 Firebase Setup:')
    console.log('1. Go to https://console.firebase.google.com/')
    console.log('2. Select your project: citypulse-21')
    console.log('3. Go to Project Settings > General')
    console.log('4. Copy the Firebase config values')
    console.log('5. Go to Project Settings > Service Accounts')
    console.log('6. Generate new private key and download JSON file')

    await this.askQuestion(
      'Press Enter when you have the Firebase config ready...'
    )
  }

  async setupGCPCredentials() {
    console.log('\n☁️  Google Cloud Setup:')
    console.log('1. Go to https://console.cloud.google.com/')
    console.log('2. Select project: citypulse-21')
    console.log('3. Enable required APIs:')
    console.log('   - Firebase Admin SDK API')
    console.log('   - Cloud Firestore API')
    console.log('   - BigQuery API')
    console.log('   - Pub/Sub API')

    await this.askQuestion('Press Enter when APIs are enabled...')
  }

  async validateCredentials() {
    console.log('\n🔍 Validating credentials...\n')

    const envExists = fs.existsSync(this.envPath)
    console.log(`📄 .env.local file: ${envExists ? '✅ Found' : '❌ Missing'}`)

    if (!envExists) {
      console.log('Please run option 3 to copy credentials to .env.local')
      return
    }

    const envContent = fs.readFileSync(this.envPath, 'utf8')
    const envVars = this.parseEnvFile(envContent)

    // Validate Firebase credentials
    console.log('\n🔥 Firebase Credentials:')
    this.requiredCredentials.firebase.forEach(key => {
      const exists = envVars[key] && envVars[key] !== 'your_value_here'
      console.log(`   ${key}: ${exists ? '✅' : '❌'}`)
    })

    // Validate GCP credentials
    console.log('\n☁️  Google Cloud Credentials:')
    this.requiredCredentials.gcp.forEach(key => {
      const exists = envVars[key] && envVars[key] !== 'your_value_here'
      console.log(`   ${key}: ${exists ? '✅' : '❌'}`)
    })

    // Validate API credentials
    console.log('\n🌐 API Credentials:')
    this.requiredCredentials.api.forEach(key => {
      const exists = envVars[key] && envVars[key] !== 'your_value_here'
      console.log(`   ${key}: ${exists ? '✅' : '❌'}`)
    })

    // Check Firebase service account file
    const serviceAccountPath = envVars['FIREBASE_SERVICE_ACCOUNT_KEY_PATH']
    if (serviceAccountPath) {
      const fullPath = path.resolve(serviceAccountPath)
      const fileExists = fs.existsSync(fullPath)
      console.log(
        `\n🔑 Service Account File: ${fileExists ? '✅ Found' : '❌ Missing'}`
      )
      if (fileExists) {
        try {
          const serviceAccount = JSON.parse(fs.readFileSync(fullPath, 'utf8'))
          console.log(`   Project ID: ${serviceAccount.project_id}`)
          console.log(`   Client Email: ${serviceAccount.client_email}`)
        } catch (error) {
          console.log('   ❌ Invalid JSON format')
        }
      }
    }
  }

  async copyToEnv() {
    console.log('\n📋 Copying credentials to .env.local...\n')

    if (!fs.existsSync(this.credentialsPath)) {
      console.log('❌ Credentials file not found!')
      return
    }

    const credentials = fs.readFileSync(this.credentialsPath, 'utf8')

    // Filter out comments and empty lines for .env.local
    const envLines = credentials.split('\n').filter(line => {
      const trimmed = line.trim()
      return (
        trimmed &&
        !trimmed.startsWith('#') &&
        !trimmed.startsWith('//') &&
        trimmed.includes('=')
      )
    })

    const envContent = envLines.join('\n')

    // Backup existing .env.local if it exists
    if (fs.existsSync(this.envPath)) {
      const backupPath = `${this.envPath}.backup.${Date.now()}`
      fs.copyFileSync(this.envPath, backupPath)
      console.log(
        `📦 Backed up existing .env.local to ${path.basename(backupPath)}`
      )
    }

    fs.writeFileSync(this.envPath, envContent)
    console.log('✅ Credentials copied to .env.local')
    console.log(
      '📝 Please update the placeholder values with your actual credentials'
    )
  }

  async generateSecrets() {
    console.log('\n🔐 Generating secure secrets...\n')

    const secrets = {
      JWT_SECRET: this.generateRandomString(64),
      API_SECRET_KEY: this.generateRandomString(32),
      WEBHOOK_SECRET: this.generateRandomString(32),
      SESSION_SECRET: this.generateRandomString(32),
      COOKIE_SECRET: this.generateRandomString(32),
      ENCRYPTION_KEY: this.generateRandomString(32),
    }

    console.log('Generated secrets:')
    Object.entries(secrets).forEach(([key, value]) => {
      console.log(`${key}="${value}"`)
    })

    const save = await this.askQuestion(
      '\nSave these secrets to credentials file? (y/n): '
    )
    if (save.toLowerCase() === 'y') {
      let credentialsContent = fs.readFileSync(this.credentialsPath, 'utf8')

      Object.entries(secrets).forEach(([key, value]) => {
        const regex = new RegExp(`${key}="[^"]*"`, 'g')
        credentialsContent = credentialsContent.replace(
          regex,
          `${key}="${value}"`
        )
      })

      fs.writeFileSync(this.credentialsPath, credentialsContent)
      console.log('✅ Secrets saved to credentials file')
    }
  }

  generateRandomString(length) {
    const chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  parseEnvFile(content) {
    const vars = {}
    content.split('\n').forEach(line => {
      const trimmed = line.trim()
      if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
        const [key, ...valueParts] = trimmed.split('=')
        const value = valueParts.join('=').replace(/^["']|["']$/g, '')
        vars[key.trim()] = value
      }
    })
    return vars
  }

  askQuestion(question) {
    return new Promise(resolve => {
      rl.question(question, resolve)
    })
  }
}

// Run the credentials manager
if (require.main === module) {
  const manager = new CredentialsManager()
  manager.start().catch(console.error)
}

module.exports = CredentialsManager

// Make the script executable
if (require.main === module) {
  console.log('🔥 CityPulse Credentials Manager')
  console.log('Run with: node credentials/setup-credentials.js')
}
