'use client'

import { createErrorBoundaryInfo } from '@/lib/error-handler'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const errorInfo = createErrorBoundaryInfo(error)

  // Log critical global error
  console.error('Global Error:', errorInfo.errorResponse)
  return (
    <html>
      <body>
        <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center px-4">
          <div className="max-w-md w-full text-center">
            <div className="mb-8">
              <div className="text-6xl mb-4">💥</div>
              <h1 className="text-2xl font-semibold text-gray-900 mb-2">Critical Error</h1>
              <p className="text-gray-600 mb-4">
                {errorInfo.userMessage}
              </p>
              {error.digest && (
                <p className="text-sm text-gray-500 mb-4">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
            
            <div className="space-y-4">
              <button
                onClick={reset}
                className="inline-block bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors mr-4"
              >
                Try Again
              </button>
              
              <button
                onClick={() => window.location.href = '/'}
                className="inline-block bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      </body>
    </html>
  )
}
