/**
 * Tests for Firebase configuration validation
 */

describe('Firebase Configuration', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  it('should throw error in production with missing config', () => {
    const originalEnv = process.env.NODE_ENV
    const originalApiKey = process.env.NEXT_PUBLIC_FIREBASE_API_KEY

    // Mock environment
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'production',
      writable: true,
      configurable: true,
    })
    delete process.env.NEXT_PUBLIC_FIREBASE_API_KEY

    expect(() => {
      require('../../src/services/firebase/config')
    }).toThrow('Missing required Firebase configuration in production')

    // Restore environment
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: originalEnv,
      writable: true,
      configurable: true,
    })
    if (originalApiKey) {
      process.env.NEXT_PUBLIC_FIREBASE_API_KEY = originalApiKey
    }
  })

  it('should use mock config in development with missing env vars', () => {
    const originalEnv = process.env.NODE_ENV

    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'development',
      writable: true,
      configurable: true,
    })
    delete process.env.NEXT_PUBLIC_FIREBASE_API_KEY

    // Should not throw in development
    expect(() => {
      require('../../src/services/firebase/config')
    }).not.toThrow()

    // Restore environment
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: originalEnv,
      writable: true,
      configurable: true,
    })
  })

  it('should throw error in production with mock values', () => {
    const originalEnv = process.env.NODE_ENV
    const originalVars = {
      NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:
        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      NEXT_PUBLIC_FIREBASE_PROJECT_ID:
        process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:
        process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
      NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:
        process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
      NEXT_PUBLIC_FIREBASE_APP_ID: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    }

    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'production',
      writable: true,
      configurable: true,
    })
    process.env.NEXT_PUBLIC_FIREBASE_API_KEY = 'mock-api-key'
    process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN =
      'citypulse-21.firebaseapp.com'
    process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID = 'citypulse-21'
    process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'citypulse-21.appspot.com'
    process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = '123456789012'
    process.env.NEXT_PUBLIC_FIREBASE_APP_ID = '1:123456789012:web:abcdef123456'

    expect(() => {
      require('../../src/services/firebase/config')
    }).toThrow('Mock Firebase configuration detected in production')

    // Restore environment
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: originalEnv,
      writable: true,
      configurable: true,
    })
    Object.keys(originalVars).forEach(key => {
      if (originalVars[key as keyof typeof originalVars]) {
        process.env[key] = originalVars[key as keyof typeof originalVars]
      } else {
        delete process.env[key]
      }
    })
  })

  it('should accept valid config in production', () => {
    const originalEnv = process.env.NODE_ENV
    const originalVars = {
      NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:
        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      NEXT_PUBLIC_FIREBASE_PROJECT_ID:
        process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET:
        process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
      NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID:
        process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
      NEXT_PUBLIC_FIREBASE_APP_ID: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    }

    Object.defineProperty(process.env, 'NODE_ENV', {
      value: 'production',
      writable: true,
      configurable: true,
    })
    process.env.NEXT_PUBLIC_FIREBASE_API_KEY =
      'AIzaSyDOCAbC123dEf456GhI789jKl01MnOpQrS'
    process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN =
      'real-project.firebaseapp.com'
    process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID = 'real-project'
    process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'real-project.appspot.com'
    process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = '987654321098'
    process.env.NEXT_PUBLIC_FIREBASE_APP_ID = '1:987654321098:web:realappid123'

    // Should not throw with valid config
    expect(() => {
      require('../../src/services/firebase/config')
    }).not.toThrow()

    // Restore environment
    Object.defineProperty(process.env, 'NODE_ENV', {
      value: originalEnv,
      writable: true,
      configurable: true,
    })
    Object.keys(originalVars).forEach(key => {
      if (originalVars[key as keyof typeof originalVars]) {
        process.env[key] = originalVars[key as keyof typeof originalVars]
      } else {
        delete process.env[key]
      }
    })
  })
})
