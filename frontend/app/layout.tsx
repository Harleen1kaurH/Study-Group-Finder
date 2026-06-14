import type { Metadata } from "next"; //gives autocompletion for when writing metadata
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./lib/auth";


//Load the Geist font, make it available through the CSS variable 
//--font-geist-sans, and only download the Latin characters to keep things efficient.
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Study Group Finder",
  description: "Find and join study groups for your courses",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {/* AuthProvider wraps the entire app so every page can access user state */}
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
