'use client'

/**
 * Dashboard page — /dashboard
 *
 * Main page after login. Shows:
 * - Navbar with user name and logout button
 * - List of all study groups (filterable by course code)
 * - Create Group button that opens a modal
 * - Notifications panel on the right
 *
 * Redirects to /login if not authenticated.
 */

import { useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../lib/auth'
import { getGroups } from '../lib/api'
import GroupCard from './GroupCard'
import CreateGroupModal from './CreateGroupModal'
import NotificationsPanel from './NotificationsPanel'
import UpcomingSessionsPanel from './UpcomingSessionsPanel'

interface Group {
    id: string
    name: string
    course_id: string
    owner_id: string
    max_size: number
    created_at: string
    is_member: boolean
}

export default function DashboardPage() {
    const { user, loading: authLoading, logout } = useAuth()
    const router = useRouter()

    const [groups, setGroups] = useState<Group[]>([])
    const [groupsLoading, setGroupsLoading] = useState(true)
    const [search, setSearch] = useState('')           // course code filter
    const [showModal, setShowModal] = useState(false)  // create group modal visibility

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login')
        }
    }, [user, authLoading, router])

    // Wrapped in useCallback so the identity only changes when the search
    // filter changes; that lets the effect below declare it as a dependency
    // without re-fetching on every render.
    const fetchGroups = useCallback(async () => {
        setGroupsLoading(true)
        try {
            const data = await getGroups(search || undefined)
            setGroups(data)
        } catch (err) {
            console.error(err)
        } finally {
            setGroupsLoading(false)
        }
    }, [search])

    // Fetch groups whenever the search filter changes. This is the standard
    // fetch-on-mount/on-change pattern; the newer set-state-in-effect lint
    // rule flags it because fetchGroups sets loading state before its first
    // await, but there's no external system here to subscribe to instead.
    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        fetchGroups()
    }, [fetchGroups])

    async function handleLogout() {
        await logout()
        router.push('/login')
    }

    // Show nothing while auth state is loading
    if (authLoading || !user) return null

    return (
        <div className="min-h-screen bg-gray-50">

            {/* Navbar */}
            <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
                <h1 className="text-lg font-bold text-gray-900">Study Group Finder</h1>
                <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">Hi, {user.name}</span>
                    <button
                        onClick={handleLogout}
                        className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                    >
                        Logout
                    </button>
                </div>
            </nav>

            {/* Main content */}
            <div className="max-w-6xl mx-auto px-6 py-8 flex gap-6">

                {/* Left column — groups list */}
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-gray-900">Study Groups</h2>
                        <button
                            onClick={() => setShowModal(true)}
                            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                            + Create Group
                        </button>
                    </div>

                    {/* Course code search filter */}
                    <input
                        type="text"
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        placeholder="Filter by course code (e.g. CS101)"
                        className="w-full mb-4 rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    />

                    {/* Groups list */}
                    {groupsLoading ? (
                        <p className="text-sm text-gray-400">Loading groups...</p>
                    ) : groups.length === 0 ? (
                        <p className="text-sm text-gray-400">No groups found.</p>
                    ) : (
                        <div className="flex flex-col gap-3">
                            {groups.map(group => (
                                <GroupCard
                                    key={group.id}
                                    group={group}
                                    currentUserId={user.id}
                                    onJoined={fetchGroups}  // refresh list after joining
                                />
                            ))}
                        </div>
                    )}
                </div>

                {/* Right column — upcoming sessions + notifications */}
                <div className="w-72 shrink-0 flex flex-col gap-6">
                    <UpcomingSessionsPanel />
                    <NotificationsPanel />
                </div>
            </div>

            {/* Create Group modal — only rendered when showModal is true */}
            {showModal && (
                <CreateGroupModal
                    onCreated={fetchGroups}
                    onClose={() => setShowModal(false)}
                />
            )}
        </div>
    )
}
