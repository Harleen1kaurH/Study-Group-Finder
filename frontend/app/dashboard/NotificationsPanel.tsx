'use client'

/**
 * NotificationsPanel.tsx — displays the logged-in user's notifications.
 *
 * Fetches notifications on mount and displays them newest first.
 * Shows a placeholder if there are no notifications.
 */

import { useEffect, useState } from 'react'
import { getNotifications } from '../lib/api'

interface Notification {
    id: string
    type: string
    message: string
    created_at: string
}

export default function NotificationsPanel() {
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [loading, setLoading] = useState(true)

    // Fetch notifications on mount
    useEffect(() => {
        getNotifications()
            .then(setNotifications)
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    return (
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-3">Notifications</h2>

            {loading && (
                <p className="text-sm text-gray-400">Loading...</p>
            )}

            {!loading && notifications.length === 0 && (
                <p className="text-sm text-gray-400">No notifications yet.</p>
            )}

            {/* Notification list */}
            <ul className="flex flex-col gap-2">
                {notifications.map(n => (
                    <li key={n.id} className="rounded-lg bg-gray-50 px-3 py-2">
                        <p className="text-sm text-gray-800">{n.message}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                            {new Date(n.created_at).toLocaleString()}
                        </p>
                    </li>
                ))}
            </ul>
        </div>
    )
}
