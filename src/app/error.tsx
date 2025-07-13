'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { createErrorBoundaryInfo } from '@/lib/error-handler'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  const errorInfo = createErrorBoundaryInfo(error)

  useEffect(() => {
    // Log the error using standardized error handler
    console.error('Page Error:', errorInfo.errorResponse)
  }, [error, errorInfo])

  return (
    <div className='min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center px-4'>
      <div className='max-w-md w-full text-center'>
        <div className='mb-8'>
          <div className='text-6xl mb-4'>⚠️</div>
          <h1 className='text-2xl font-semibold text-gray-900 mb-2'>
            Something went wrong!
          </h1>
          <p className='text-gray-600 mb-4'>{errorInfo.userMessage}</p>
          {error.digest && (
            <p className='text-sm text-gray-500 mb-4'>
              Error ID: {error.digest}
            </p>
          )}
          {process.env.NODE_ENV === 'development' && (
            <details className='text-left text-sm text-gray-500 mb-4'>
              <summary className='cursor-pointer'>
                Error Details (Development)
              </summary>
              <pre className='mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto'>
                {JSON.stringify(errorInfo.errorResponse, null, 2)}
              </pre>
            </details>
          )}
        </div>

        <div className='space-y-4'>
          {errorInfo.shouldRetry && (
            <button
              onClick={reset}
              className='inline-block bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors mr-4'
            >
              Try Again
            </button>
          )}

          <Link
            href='/'
            className='inline-block bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors'
          >
            Go Home
          </Link>
        </div>
      </div>
    </div>
  )
}
