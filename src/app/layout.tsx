import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AsyncErrorBoundary } from "@/components/common/ErrorBoundary";

export const metadata: Metadata = {
  title: "CityPulse - Urban Issue Tracking Platform",
  description: "Community-driven urban issue reporting and resolution platform with AI-powered insights",
  keywords: "urban planning, issue tracking, community reporting, smart city, AI analytics",
  authors: [{ name: "CityPulse Team" }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AsyncErrorBoundary
          onError={(error, errorInfo) => {
            // Log error for monitoring
            console.error("Root layout error:", error, errorInfo);
          }}
        >
          {children}
        </AsyncErrorBoundary>
      </body>
    </html>
  );
}
