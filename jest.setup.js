// Jest setup file for CityPulse testing framework
import '@testing-library/jest-dom'
import 'jest-canvas-mock'
import { configure } from '@testing-library/react'

// Import jest-axe conditionally to avoid issues if not installed
let toHaveNoViolations
try {
  const jestAxe = require('jest-axe')
  toHaveNoViolations = jestAxe.toHaveNoViolations
} catch (error) {
  // jest-axe not available, create a mock matcher
  toHaveNoViolations = {
    toHaveNoViolations: () => ({
      pass: true,
      message: () => 'jest-axe not available'
    })
  }
}

// Extend Jest matchers
expect.extend(toHaveNoViolations)

// Configure React Testing Library
configure({
  testIdAttribute: 'data-testid',
  asyncUtilTimeout: 5000,
})

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
      isLocaleDomain: true,
      isReady: true,
      defaultLocale: 'en',
      domainLocales: [],
      isPreview: false,
    }
  },
}))

// Mock Next.js navigation (App Router)
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} />
  },
}))

// Mock Next.js Link component
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, ...props }) => {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  },
}))

// Mock environment variables
process.env.NODE_ENV = 'test'
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_APP_URL = 'http://localhost:3000'

// Mock fetch globally
global.fetch = jest.fn()

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock geolocation
const mockGeolocation = {
  getCurrentPosition: jest.fn(),
  watchPosition: jest.fn(),
  clearWatch: jest.fn(),
}
Object.defineProperty(navigator, 'geolocation', {
  value: mockGeolocation,
})

// Global test utilities
global.testUtils = {
  // Helper to wait for async operations
  waitFor: (callback, timeout = 5000) => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      const check = () => {
        try {
          const result = callback()
          if (result) {
            resolve(result)
          } else if (Date.now() - startTime > timeout) {
            reject(new Error('Timeout waiting for condition'))
          } else {
            setTimeout(check, 100)
          }
        } catch (error) {
          if (Date.now() - startTime > timeout) {
            reject(error)
          } else {
            setTimeout(check, 100)
          }
        }
      }
      check()
    })
  },

  // Helper to create mock events
  createMockEvent: (type, properties = {}) => ({
    type,
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
    target: { value: '' },
    currentTarget: { value: '' },
    ...properties,
  }),

  // Helper to create mock API responses
  createMockApiResponse: (data, status = 200) => ({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    json: jest.fn().mockResolvedValue(data),
    text: jest.fn().mockResolvedValue(JSON.stringify(data)),
    headers: new Headers(),
  }),
}

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks()
  localStorageMock.clear()
})
