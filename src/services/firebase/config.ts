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
 * Validate Firebase configuration
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
    console.warn('Missing Firebase configuration keys:', missingKeys)
    
    // Use default/mock configuration for development
    if (process.env.NODE_ENV === 'development') {
      return {
        apiKey: 'mock-api-key',
        authDomain: 'citypulse-21.firebaseapp.com',
        projectId: 'citypulse-21',
        storageBucket: 'citypulse-21.appspot.com',
        messagingSenderId: '123456789012',
        appId: '1:123456789012:web:abcdef123456',
      }
    } else {
      throw new Error(`Missing required Firebase configuration: ${missingKeys.join(', ')}`)
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
    if (process.env.NODE_ENV === 'development' && !auth.config.emulator) {
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
let app: FirebaseApp
let auth: Auth
let firestore: Firestore
let storage: FirebaseStorage

try {
  app = initializeFirebaseApp()
  auth = initializeFirebaseAuth(app)
  firestore = initializeFirestore(app)
  storage = initializeFirebaseStorage(app)
} catch (error) {
  console.error('Firebase initialization failed:', error)
  
  // In development, we can continue with mock services
  if (process.env.NODE_ENV === 'development') {
    console.warn('Continuing with limited Firebase functionality')
  } else {
    throw error
  }
}

// Export Firebase services
export { app, auth, firestore, storage }

// Export configuration for debugging
export const firebaseConfig = validateFirebaseConfig()

// Export initialization status
export const isFirebaseInitialized = !!app && !!auth

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
