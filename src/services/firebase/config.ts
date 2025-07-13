/**
 * Firebase Configuration
 * Initializes Firebase services with proper error handling and validation
 */

import { initializeApp, getApps, FirebaseApp } from 'firebase/app'
import { getAuth, Auth, connectAuthEmulator } from 'firebase/auth'
import { getFirestore, Firestore, connectFirestoreEmulator } from 'firebase/firestore'
import { getStorage, FirebaseStorage, connectStorageEmulator } from 'firebase/storage'

/**
 * Firebase configuration interface
 */
interface FirebaseConfig {
  apiKey: string
  authDomain: string
  projectId: string
  storageBucket: string
  messagingSenderId: string
  appId: string
}

/**
 * Get mock Firebase configuration for development
 */
function getMockFirebaseConfig(): FirebaseConfig {
  return {
    apiKey: 'mock-api-key',
    authDomain: 'citypulse-21.firebaseapp.com',
    projectId: 'citypulse-21',
    storageBucket: 'citypulse-21.appspot.com',
    messagingSenderId: '123456789012',
    appId: '1:123456789012:web:abcdef123456',
  }
}

/**
 * Validate Firebase configuration with strict production checks
 */
function validateFirebaseConfig(): FirebaseConfig {
  const config = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  }

  // Check for missing configuration
  const missingKeys = Object.entries(config)
    .filter(([key, value]) => !value)
    .map(([key]) => key)

  if (missingKeys.length > 0) {
    // Strict validation for production environment
    if (process.env.NODE_ENV === 'production') {
      throw new Error(
        `Missing required Firebase configuration in production: ${missingKeys.join(', ')}. ` +
        'All Firebase environment variables must be set in production.'
      )
    }

    // Log warning for development
    console.warn('Missing Firebase configuration keys:', missingKeys)
    console.warn('Using mock Firebase configuration for development')

    // Only allow mock values in development
    return getMockFirebaseConfig()
  }

  // Additional validation for production
  if (process.env.NODE_ENV === 'production') {
    // Validate that we're not using mock values in production
    const mockValues = ['mock-api-key', '123456789012', '1:123456789012:web:abcdef123456']
    const hasMockValues = Object.values(config).some(value =>
      mockValues.includes(value as string)
    )

    if (hasMockValues) {
      throw new Error(
        'Mock Firebase configuration detected in production. ' +
        'Please set real Firebase configuration values.'
      )
    }

    // Validate API key format (basic check)
    if (config.apiKey && !config.apiKey.startsWith('AIza')) {
      console.warn('Firebase API key format may be invalid')
    }
  }

  return config as FirebaseConfig
}

/**
 * Initialize Firebase app
 */
function initializeFirebaseApp(): FirebaseApp {
  // Check if Firebase is already initialized
  if (getApps().length > 0) {
    return getApps()[0]
  }

  const config = validateFirebaseConfig()
  
  try {
    const app = initializeApp(config)
    console.log('Firebase initialized successfully')
    return app
  } catch (error) {
    console.error('Failed to initialize Firebase:', error)
    throw error
  }
}

/**
 * Initialize Firebase Auth
 */
function initializeFirebaseAuth(app: FirebaseApp): Auth {
  try {
    const auth = getAuth(app)
    
    // Connect to Auth emulator in development
    if (process.env.NODE_ENV === 'development') {
      try {
        connectAuthEmulator(auth, 'http://localhost:9099', { disableWarnings: true })
        console.log('Connected to Firebase Auth emulator')
      } catch (error) {
        console.warn('Could not connect to Firebase Auth emulator:', error)
      }
    }
    
    return auth
  } catch (error) {
    console.error('Failed to initialize Firebase Auth:', error)
    throw error
  }
}

/**
 * Initialize Firestore
 */
function initializeFirestore(app: FirebaseApp): Firestore {
  try {
    const firestore = getFirestore(app)
    
    // Connect to Firestore emulator in development
    if (process.env.NODE_ENV === 'development') {
      try {
        connectFirestoreEmulator(firestore, 'localhost', 8080)
        console.log('Connected to Firestore emulator')
      } catch (error) {
        console.warn('Could not connect to Firestore emulator:', error)
      }
    }
    
    return firestore
  } catch (error) {
    console.error('Failed to initialize Firestore:', error)
    throw error
  }
}

/**
 * Initialize Firebase Storage
 */
function initializeFirebaseStorage(app: FirebaseApp): FirebaseStorage {
  try {
    const storage = getStorage(app)
    
    // Connect to Storage emulator in development
    if (process.env.NODE_ENV === 'development') {
      try {
        connectStorageEmulator(storage, 'localhost', 9199)
        console.log('Connected to Firebase Storage emulator')
      } catch (error) {
        console.warn('Could not connect to Firebase Storage emulator:', error)
      }
    }
    
    return storage
  } catch (error) {
    console.error('Failed to initialize Firebase Storage:', error)
    throw error
  }
}

// Initialize Firebase services
let app: FirebaseApp | undefined
let auth: Auth | undefined
let firestore: Firestore | undefined
let storage: FirebaseStorage | undefined

try {
  app = initializeFirebaseApp()
  auth = initializeFirebaseAuth(app)
  firestore = initializeFirestore(app)
  storage = initializeFirebaseStorage(app)

  // Log successful initialization
  if (process.env.NODE_ENV === 'development') {
    console.log('Firebase services initialized successfully')
  }
} catch (error) {
  console.error('Firebase initialization failed:', error)

  // In development, we can continue with limited functionality
  if (process.env.NODE_ENV === 'development') {
    console.warn('Continuing with limited Firebase functionality in development mode')
    console.warn('Some features may not work properly without real Firebase configuration')
  } else {
    // In production, Firebase failure is critical
    console.error('Firebase initialization failed in production - this is a critical error')
    throw new Error(`Firebase initialization failed in production: ${error}`)
  }
}

// Export Firebase services (may be undefined if initialization failed)
export { app, auth, firestore, storage }

// Export configuration for debugging
export const firebaseConfig = validateFirebaseConfig()

// Export initialization status
export const isFirebaseInitialized = () => !!app && !!auth

// Health check function
export function checkFirebaseHealth(): {
  app: boolean
  auth: boolean
  firestore: boolean
  storage: boolean
} {
  return {
    app: !!app,
    auth: !!auth,
    firestore: !!firestore,
    storage: !!storage,
  }
}
