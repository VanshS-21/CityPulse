import Link from 'next/link'

export default function NotFound() {
  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4'>
      <div className='max-w-md w-full text-center'>
        <div className='mb-8'>
          <h1 className='text-9xl font-bold text-blue-600 mb-4'>404</h1>
          <h2 className='text-2xl font-semibold text-gray-900 mb-2'>
            Page Not Found
          </h2>
          <p className='text-gray-600'>
            Sorry, we couldn&apos;t find the page you&apos;re looking for.
          </p>
        </div>

        <div className='space-y-4'>
          <Link
            href='/'
            className='inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors'
          >
            Go Home
          </Link>

          <div className='text-sm text-gray-500'>
            <Link
              href='/dashboard'
              className='text-blue-600 hover:text-blue-700 mx-2'
            >
              Dashboard
            </Link>
            |
            <Link
              href='/report'
              className='text-blue-600 hover:text-blue-700 mx-2'
            >
              Report Issue
            </Link>
            |
            <Link
              href='/social'
              className='text-blue-600 hover:text-blue-700 mx-2'
            >
              Social Feed
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
