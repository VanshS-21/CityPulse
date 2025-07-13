import type { Metadata, Viewport } from 'next'
import { Inter, Roboto_Flex } from 'next/font/google'
import { AppProviders } from '@/providers/app-providers'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const robotoFlex = Roboto_Flex({
  subsets: ['latin'],
  variable: '--font-roboto-flex',
})

export const metadata: Metadata = {
  title: 'CityPulse - Urban Intelligence Platform',
  description: 'Modern urban intelligence platform for smarter cities',
  keywords: 'urban planning, smart city, city management, urban analytics',
  authors: [{ name: 'CityPulse Team' }],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang='en' className='dark'>
      <body
        className={`${inter.variable} ${robotoFlex.variable} antialiased min-h-screen bg-background font-sans text-foreground`}
      >
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  )
}
