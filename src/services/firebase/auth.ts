/**
 * Firebase Authentication Service
 * Provides comprehensive authentication functionality with proper error handling
 */

import { 
  Auth, 
  User, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  sendPasswordResetEmail,
  sendEmailVerification,
  GoogleAuthProvider,
  signInWithPopup,
  UserCredential
} from 'firebase/auth'
import { auth } from './config'
import { apiGateway } from '@/lib/api-gateway'

export interface AuthUser {
  id: string
  email: string | null
  name: string | null
  avatar?: string | null
  role: 'citizen' | 'admin' | 'moderator'
  emailVerified: boolean
  createdAt: Date
  lastLoginAt: Date
}

export interface AuthError {
  code: string
  message: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  password: string
  name: string
}

/**
 * Firebase Authentication Service Class
 */
export class FirebaseAuthService {
  private auth: Auth
  private currentUser: AuthUser | null = null
  private authStateListeners: ((user: AuthUser | null) => void)[] = []

  constructor() {
    this.auth = auth
    this.initializeAuthStateListener()
  }

  /**
   * Initialize auth state listener
   */
  private initializeAuthStateListener(): void {
    onAuthStateChanged(this.auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const authUser = await this.transformFirebaseUser(firebaseUser)
          this.currentUser = authUser
          
          // Update API gateway auth token
          const token = await firebaseUser.getIdToken()
          apiGateway.setAuthToken(token)
          
          // Notify listeners
          this.notifyAuthStateListeners(authUser)
        } catch (error) {
          console.error('Error transforming Firebase user:', error)
          this.currentUser = null
          apiGateway.setAuthToken(null)
          this.notifyAuthStateListeners(null)
        }
      } else {
        this.currentUser = null
        apiGateway.setAuthToken(null)
        this.notifyAuthStateListeners(null)
      }
    })
  }

  /**
   * Transform Firebase user to AuthUser
   */
  private async transformFirebaseUser(firebaseUser: User): Promise<AuthUser> {
    // Get additional user data from backend if available
    let role: 'citizen' | 'admin' | 'moderator' = 'citizen'
    
    try {
      // Try to get user profile from backend
      const userProfile = await apiGateway.get(`/users/${firebaseUser.uid}`)
      role = userProfile.role || 'citizen'
    } catch (error) {
      // If backend call fails, default to citizen role
      console.warn('Could not fetch user profile from backend:', error)
    }

    return {
      id: firebaseUser.uid,
      email: firebaseUser.email,
      name: firebaseUser.displayName,
      avatar: firebaseUser.photoURL,
      role,
      emailVerified: firebaseUser.emailVerified,
      createdAt: firebaseUser.metadata.creationTime ? new Date(firebaseUser.metadata.creationTime) : new Date(),
      lastLoginAt: firebaseUser.metadata.lastSignInTime ? new Date(firebaseUser.metadata.lastSignInTime) : new Date(),
    }
  }

  /**
   * Notify auth state listeners
   */
  private notifyAuthStateListeners(user: AuthUser | null): void {
    this.authStateListeners.forEach(listener => listener(user))
  }

  /**
   * Add auth state change listener
   */
  onAuthStateChange(callback: (user: AuthUser | null) => void): () => void {
    this.authStateListeners.push(callback)
    
    // Return unsubscribe function
    return () => {
      const index = this.authStateListeners.indexOf(callback)
      if (index > -1) {
        this.authStateListeners.splice(index, 1)
      }
    }
  }

  /**
   * Get current user
   */
  getCurrentUser(): AuthUser | null {
    return this.currentUser
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.currentUser !== null
  }

  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthUser> {
    try {
      const userCredential = await signInWithEmailAndPassword(
        this.auth,
        credentials.email,
        credentials.password
      )
      
      const authUser = await this.transformFirebaseUser(userCredential.user)
      
      // Track login event
      this.trackAuthEvent('login', authUser.id)
      
      return authUser
    } catch (error: any) {
      throw this.transformFirebaseError(error)
    }
  }

  /**
   * Register new user
   */
  async register(credentials: RegisterCredentials): Promise<AuthUser> {
    try {
      const userCredential = await createUserWithEmailAndPassword(
        this.auth,
        credentials.email,
        credentials.password
      )

      // Update user profile with name
      await updateProfile(userCredential.user, {
        displayName: credentials.name
      })

      // Send email verification
      await sendEmailVerification(userCredential.user)

      const authUser = await this.transformFirebaseUser(userCredential.user)
      
      // Create user profile in backend
      try {
        await apiGateway.post('/users', {
          id: authUser.id,
          email: authUser.email,
          name: authUser.name,
          role: 'citizen',
        })
      } catch (error) {
        console.warn('Could not create user profile in backend:', error)
      }
      
      // Track registration event
      this.trackAuthEvent('register', authUser.id)
      
      return authUser
    } catch (error: any) {
      throw this.transformFirebaseError(error)
    }
  }

  /**
   * Login with Google
   */
  async loginWithGoogle(): Promise<AuthUser> {
    try {
      const provider = new GoogleAuthProvider()
      const userCredential = await signInWithPopup(this.auth, provider)
      
      const authUser = await this.transformFirebaseUser(userCredential.user)
      
      // Track login event
      this.trackAuthEvent('google_login', authUser.id)
      
      return authUser
    } catch (error: any) {
      throw this.transformFirebaseError(error)
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      const userId = this.currentUser?.id
      await signOut(this.auth)
      
      // Track logout event
      if (userId) {
        this.trackAuthEvent('logout', userId)
      }
    } catch (error: any) {
      throw this.transformFirebaseError(error)
    }
  }

  /**
   * Send password reset email
   */
  async resetPassword(email: string): Promise<void> {
    try {
      await sendPasswordResetEmail(this.auth, email)
    } catch (error: any) {
      throw this.transformFirebaseError(error)
    }
  }

  /**
   * Send email verification
   */
  async sendEmailVerification(): Promise<void> {
    try {
      if (!this.auth.currentUser) {
        throw new Error('No authenticated user')
      }
      await sendEmailVerification(this.auth.currentUser)
    } catch (error: any) {
      throw this.transformFirebaseError(error)
    }
  }

  /**
   * Get current user's ID token
   */
  async getIdToken(): Promise<string | null> {
    try {
      if (!this.auth.currentUser) {
        return null
      }
      return await this.auth.currentUser.getIdToken()
    } catch (error) {
      console.error('Error getting ID token:', error)
      return null
    }
  }

  /**
   * Transform Firebase error to AuthError
   */
  private transformFirebaseError(error: any): AuthError {
    const errorMap: Record<string, string> = {
      'auth/user-not-found': 'No user found with this email address',
      'auth/wrong-password': 'Incorrect password',
      'auth/email-already-in-use': 'An account with this email already exists',
      'auth/weak-password': 'Password should be at least 6 characters',
      'auth/invalid-email': 'Invalid email address',
      'auth/user-disabled': 'This account has been disabled',
      'auth/too-many-requests': 'Too many failed attempts. Please try again later',
      'auth/network-request-failed': 'Network error. Please check your connection',
    }

    return {
      code: error.code || 'auth/unknown-error',
      message: errorMap[error.code] || error.message || 'An unknown error occurred'
    }
  }

  /**
   * Track authentication events
   */
  private trackAuthEvent(event: string, userId: string): void {
    try {
      // Send analytics event (non-blocking)
      apiGateway.post('/analytics/events', {
        event_type: `auth_${event}`,
        user_id: userId,
        timestamp: new Date().toISOString(),
      }).catch(error => {
        console.warn('Failed to track auth event:', error)
      })
    } catch (error) {
      console.warn('Failed to track auth event:', error)
    }
  }
}

// Export singleton instance
export const firebaseAuth = new FirebaseAuthService()

// Export types
export type { AuthUser, AuthError, LoginCredentials, RegisterCredentials }
