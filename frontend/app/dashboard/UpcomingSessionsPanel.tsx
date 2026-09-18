'use client'

/**
 * UpcomingSessionsPanel.tsx — "upcoming events" box for the dashboard.
 *
 * Same simple pattern as NotificationsPanel: fetch once on mount, no
 * real-time updates, just a plain list. Shows only CONFIRMED sessions
 * (status='scheduled') with a future date/time, across every group the
 * logged-in user belongs to — soonest first.
 */

import { useEffect, useState } from 'react'
import { getUpcomingSessions } from '../lib/api'

interface UpcomingSession {
    session_id: string
    session_name: string
    group_id: string
    group_name: string
    course_code: string
    slot_date: string       // e.g. "2026-09-20"
    start_time: string      // e.g. "14:30:00"
    duration_minutes: number
    location: string | null
}

// Same date/time formatting approach as the group page's formatSlotRange —
// combine slot_date + start_time, add duration_minutes for the end time.
function formatWhen(s: UpcomingSession): string {
    const start = new Date(`${s.slot_date}T${s.start_time}`)
    const end = new Date(start.getTime() + s.duration_minutes * 60000)
    const dateLabel = start.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
    const startLabel = start.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
    const endLabel = end.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
    return `${dateLabel}, ${startLabel} – ${endLabel}`
}

export default function UpcomingSessionsPanel() {
    const [sessions, setSessions] = useState<UpcomingSession[]>([])
    const [loading, setLoading] = useState(true)

    // Fetch on mount — matches NotificationsPanel's fetch-once, no-live-updates pattern
    useEffect(() => {
        getUpcomingSessions()
            .then(setSessions)
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    return (
        <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-3">Upcoming Sessions</h2>

            {loading && (
                <p className="text-sm text-gray-400">Loading...</p>
            )}

            {!loading && sessions.length === 0 && (
                <p className="text-sm text-gray-400">No upcoming sessions.</p>
            )}

            <ul className="flex flex-col gap-2">
                {sessions.map(s => (
                    <li key={s.session_id} className="rounded-lg bg-blue-50 px-3 py-2">
                        <p className="text-sm font-medium text-gray-900">{s.session_name}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{s.group_name} ({s.course_code})</p>
                        <p className="text-xs text-blue-600 font-medium mt-0.5">{formatWhen(s)}</p>
                        {s.location && (
                            <p className="text-xs text-gray-400 mt-0.5">{s.location}</p>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    )
}
