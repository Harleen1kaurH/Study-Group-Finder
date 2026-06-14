'use client'

/**
 * Register page — /register
 *
 * Renders a registration form. On submit:
 * 1. Calls register() from api.ts to create the account
 * 2. Calls login() from useAuth() to auto-log in
 * 3. Redirects to /dashboard on success
 * 4. Shows error message on failure
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '../lib/auth'
import { register } from '../lib/api'

export default function RegisterPage() {
    const { login } = useAuth()
    const router = useRouter()

    // Form field values
    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    // UI state
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function handleSubmit(e: React.FormEvent) {
        // Prevent default browser form submission
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            // Create the account
            await register(email, password, name)

            // Auto-login after registration
            await login(email, password)

            // Redirect to dashboard
            router.push('/dashboard')
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Registration failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="w-full max-w-md bg-white rounded-2xl shadow-md p-8">

                {/* App title */}
                <h1 className="text-2xl font-bold text-gray-900 mb-1">Study Group Finder</h1>
                <p className="text-gray-500 mb-6">Create your account</p>

                {/* Error message — only shown if error is not null */}
                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    {/* Name field */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={e => setName(e.target.value)}
                            required
                            placeholder="Your name"
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

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

                    {/* Submit button */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="mt-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Creating account...' : 'Sign up'}
                    </button>
                </form>

                {/* Link to login page */}
                <p className="mt-6 text-center text-sm text-gray-500">
                    Already have an account?{' '}
                    <Link href="/login" className="font-medium text-blue-600 hover:underline">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    )
}
