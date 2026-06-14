'use client'

/**
 * Home page — /
 *
 * Just a redirect:
 * - If logged in → /dashboard
 * - If not logged in → /login
 * - While checking auth state → show nothing (avoid flash)
 */

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from './lib/auth'

export default function Home() {
    const { user, loading } = useAuth()
    const router = useRouter()

    useEffect(() => {
        // Wait until auth state is resolved before redirecting
        if (loading) return

        if (user) {
            router.push('/dashboard')
        } else {
            router.push('/login')
        }
    }, [user, loading, router])

    // Render nothing while redirecting
    return null
}
