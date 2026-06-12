'use client'

/**
 * auth.tsx — authentication context
 *
 * Provides user state and auth functions (login, logout) to the entire app.
 * Wrap the app with <AuthProvider> in layout.tsx to enable this.
 *
 * Usage in any component:
 *   const { user, login, logout, loading } = useAuth()
 */

import { createContext, useContext, useEffect, useState } from 'react'
import { login as apiLogin, logout as apiLogout, getMe } from './api'

// Shape of the user object returned by the backend
interface User {
    id: string
    email: string
    name: string
    bio: string | null
    availability: string | null
    email_notifications: boolean
    created_at: string
}

// Shape of the auth context
interface AuthContextType {
    user: User | null          // null means not logged in
    loading: boolean           // true while checking for existing session on load
    login: (email: string, password: string) => Promise<void>
    logout: () => Promise<void>
}

// Create the context with a default value of null
const AuthContext = createContext<AuthContextType | null>(null)


export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true) // start true — check for existing session

    // On app load, check if a token exists in localStorage and fetch the current user
    useEffect(() => {
        const token = localStorage.getItem('token')
        if (token) {
            // Token exists — fetch the user profile to restore the session
            getMe()
                .then(setUser)
                .catch(() => {
                    // Token is invalid or expired — clear it
                    localStorage.removeItem('token')
                })
                .finally(() => setLoading(false))
        } else {
            // No token — not logged in
            setLoading(false)
        }
    }, [])

    // Call backend login, store the token, fetch user profile
    const login = async (email: string, password: string) => {
        const data = await apiLogin(email, password)

        // Save the token to localStorage so it persists across page refreshes
        localStorage.setItem('token', data.access_token)

        // Fetch and store the user profile
        const me = await getMe()
        setUser(me)
    }

    // Clear the token and user state
    const logout = async () => {
        await apiLogout()
        localStorage.removeItem('token')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}


// Custom hook — use this in any component to access auth state
export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used inside <AuthProvider>')
    }
    return context
}
