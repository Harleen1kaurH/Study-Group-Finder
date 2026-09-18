'use client'

/**
 * Login page — /login
 *
 * Renders a centered login form. On submit:
 * 1. Calls login() from useAuth() which hits POST /auth/login
 * 2. On success, redirects to /dashboard
 * 3. On failure, shows the error message from the backend
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '../lib/auth'

export default function LoginPage() {
    const { login } = useAuth()
    const router = useRouter()

    // Form field values
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    // UI state
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function handleSubmit(e: React.FormEvent) {
        // Prevent the browser's default form submission (which would reload the page)
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            // Call login from auth context — stores token and fetches user
            await login(email, password)
            // Redirect to dashboard on success
            router.push('/dashboard')
        } catch (err: unknown) {
            // Show the error message from the backend
            setError(err instanceof Error ? err.message : 'Login failed')
        } finally {
            // Always stop the loading state, even if an error occurred
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-md p-8">

                {/* App title */}
                <h1 className="text-2xl font-bold text-gray-900 mb-1">Study Group Finder</h1>
                <p className="text-gray-500 mb-6">Sign in to your account</p>

                {/* Error message */}
                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    {/* Email field */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required
                            placeholder="you@example.com"
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

                    {/* Password field */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

                    {/* Submit button — disabled and shows loading text while request is in flight */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="mt-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                {/* Link to register page */}
                <p className="mt-6 text-center text-sm text-gray-500">
                    Don&apos;t have an account?{' '}
                    <Link href="/register" className="font-medium text-blue-600 hover:underline">
                        Sign up
                    </Link>
                </p>
            </div>
        </div>
    )
}
