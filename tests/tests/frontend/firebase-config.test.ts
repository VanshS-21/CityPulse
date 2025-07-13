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
    process.env.NODE_ENV = 'production'
    delete process.env.NEXT_PUBLIC_FIREBASE_API_KEY
    
    expect(() => {
      require('../src/services/firebase/config')
    }).toThrow('Missing required Firebase configuration in production')
  })

  it('should use mock config in development with missing env vars', () => {
    process.env.NODE_ENV = 'development'
    delete process.env.NEXT_PUBLIC_FIREBASE_API_KEY
    
    // Should not throw in development
    expect(() => {
      require('../src/services/firebase/config')
    }).not.toThrow()
  })

  it('should throw error in production with mock values', () => {
    process.env.NODE_ENV = 'production'
    process.env.NEXT_PUBLIC_FIREBASE_API_KEY = 'mock-api-key'
    process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = 'citypulse-21.firebaseapp.com'
    process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID = 'citypulse-21'
    process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'citypulse-21.appspot.com'
    process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = '123456789012'
    process.env.NEXT_PUBLIC_FIREBASE_APP_ID = '1:123456789012:web:abcdef123456'
    
    expect(() => {
      require('../src/services/firebase/config')
    }).toThrow('Mock Firebase configuration detected in production')
  })

  it('should accept valid config in production', () => {
    process.env.NODE_ENV = 'production'
    process.env.NEXT_PUBLIC_FIREBASE_API_KEY = 'AIzaSyDOCAbC123dEf456GhI789jKl01MnOpQrS'
    process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN = 'real-project.firebaseapp.com'
    process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID = 'real-project'
    process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET = 'real-project.appspot.com'
    process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID = '987654321098'
    process.env.NEXT_PUBLIC_FIREBASE_APP_ID = '1:987654321098:web:realappid123'
    
    // Should not throw with valid config
    expect(() => {
      require('../src/services/firebase/config')
    }).not.toThrow()
  })
})
