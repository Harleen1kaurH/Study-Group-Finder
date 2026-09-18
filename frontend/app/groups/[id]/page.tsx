'use client'

/**
 * Group detail page — /groups/[id]
 *
 * Shows:
 * - Group header (name, course, max size)
 * - Members list with remove button for owner
 * - Sessions list with voting, confirm, and cancel
 * - Create Session button (members only)
 * - Leave Group button (non-owner members)
 */

import { useCallback, useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '../../lib/auth'
import {
    getGroup,
    getSessions,
    leaveGroup,
    removeMember,
    voteOnSlot,
    confirmSlot,
    cancelSession,
    deleteGroup,
} from '../../lib/api'
import CreateSessionModal from './CreateSessionModal'
import EditGroupModal from './EditGroupModal'

// Types

interface Member {
    user_id: string
    name: string
}

interface Group {
    id: string
    name: string
    course_id: string
    owner_id: string
    max_size: number
    members: Member[]
}

interface Slot {
    id: string
    slot_date: string       // e.g. "2026-09-20"
    start_time: string      // e.g. "14:30:00" (time only, no date)
    duration_minutes: number
    location: string | null
    vote_count: number | null  // null for non-owners — vote counts are owner-only
    voted_by_me: boolean       // persists across reloads — this user's own vote, always visible to them
}

interface Session {
    id: string
    name: string
    status: 'voting' | 'scheduled' | 'completed' | 'cancelled'
    voting_deadline: string  // ISO datetime — voting window is exactly 24h from proposal
    confirmed_slot_id: string | null
    slots: Slot[]
}

export default function GroupPage() {
    const { id } = useParams<{ id: string }>()
    const router = useRouter()
    const { user, loading: authLoading } = useAuth()

    const [group, setGroup] = useState<Group | null>(null)
    const [sessions, setSessions] = useState<Session[]>([])
    const [pageLoading, setPageLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [showSessionModal, setShowSessionModal] = useState(false)
    const [showEditModal, setShowEditModal] = useState(false)
    // Briefly highlighted + confirmed after a successful vote click, then cleared.
    const [justVotedSlotId, setJustVotedSlotId] = useState<string | null>(null)

    // Redirect to login if not authenticated
    useEffect(() => {
        if (!authLoading && !user) router.push('/login')
    }, [user, authLoading, router])

    // showFullPageLoading=true blanks the whole page (used only for the very first
    // load, before there's anything on screen). Refreshes triggered by an action
    // (vote, confirm, cancel, remove member) pass false so they update the data
    // in place instead of tearing down the page the user is looking at.
    // Wrapped in useCallback so the identity only changes when id changes,
    // letting the effect below declare it as a dependency safely.
    const fetchAll = useCallback(async (showFullPageLoading = true) => {
        if (showFullPageLoading) setPageLoading(true)
        try {
            const [groupData, sessionsData] = await Promise.all([
                getGroup(id),
                getSessions(id),
            ])
            setGroup(groupData)
            setSessions(sessionsData)
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to load group')
        } finally {
            if (showFullPageLoading) setPageLoading(false)
        }
    }, [id])

    // Fetch group + sessions on mount. Same fetch-on-mount pattern as the
    // dashboard page; see the note there on why set-state-in-effect is
    // suppressed rather than "fixed".
    useEffect(() => {
        if (!id) return
        // eslint-disable-next-line react-hooks/set-state-in-effect
        fetchAll()
    }, [id, fetchAll])

    async function handleLeave() {
        if (!confirm('Are you sure you want to leave this group?')) return
        try {
            await leaveGroup(id)
            router.push('/dashboard')
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to leave group')
        }
    }

    async function handleRemoveMember(userId: string) {
        if (!confirm('Remove this member?')) return
        try {
            await removeMember(id, userId)
            fetchAll(false)  // refresh quietly, don't blank the page
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to remove member')
        }
    }

    async function handleDeleteGroup() {
        if (!confirm('Delete this group? This cannot be undone.')) return
        try {
            await deleteGroup(id)
            router.push('/dashboard')
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to delete group')
        }
    }

    async function handleVote(sessionId: string, slotId: string) {
        try {
            await voteOnSlot(id, sessionId, slotId)
            fetchAll(false)
            // Highlight the slot + show a confirmation message for a few seconds
            setJustVotedSlotId(slotId)
            setTimeout(() => setJustVotedSlotId(null), 3000)
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to vote')
        }
    }

    async function handleConfirm(sessionId: string, slotId: string) {
        try {
            await confirmSlot(id, sessionId, slotId)
            fetchAll(false)
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to confirm slot')
        }
    }

    async function handleCancel(sessionId: string) {
        if (!confirm('Cancel this session?')) return
        try {
            await cancelSession(id, sessionId)
            fetchAll(false)
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to cancel session')
        }
    }

    if (authLoading || pageLoading) {
        return <div className="p-8 text-gray-400">Loading...</div>
    }

    if (error || !group) {
        return <div className="p-8 text-red-500">{error || 'Group not found'}</div>
    }

    // Derive membership status for current user
    const isOwner = group.owner_id === user?.id
    const isMember = group.members.some(m => m.user_id === user?.id)

    return (
        <div className="min-h-screen bg-gray-50">

            {/* Navbar */}
            <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-4">
                <button
                    onClick={() => router.push('/dashboard')}
                    className="text-sm text-blue-600 hover:underline"
                >
                    ← Dashboard
                </button>
                <span className="text-gray-300">|</span>
                <h1 className="text-base font-semibold text-gray-900">{group.name}</h1>
            </nav>

            <div className="max-w-4xl mx-auto px-6 py-8 flex flex-col gap-8">

                {/* Group header */}
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div className="flex items-start justify-between">
                        <div>
                            <h2 className="text-2xl font-bold text-gray-900">{group.name}</h2>
                            <p className="text-sm text-gray-500 mt-1">Max {group.max_size} members</p>
                        </div>

                        {/* Leave button — only for non-owner members */}
                        {isMember && !isOwner && (
                            <button
                                onClick={handleLeave}
                                className="rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
                            >
                                Leave Group
                            </button>
                        )}

                        {/* Edit / Delete — owner only */}
                        {isOwner && (
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setShowEditModal(true)}
                                    className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={handleDeleteGroup}
                                    className="rounded-lg border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50"
                                >
                                    Delete Group
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Members section */}
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <h3 className="text-base font-semibold text-gray-900 mb-4">
                        Members ({group.members.length}/{group.max_size})
                    </h3>
                    <ul className="flex flex-col gap-2">
                        {group.members.map(member => (
                            <li
                                key={member.user_id}
                                className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-2"
                            >
                                <span className="text-sm text-gray-800">
                                    {member.name}
                                    {/* Label the owner */}
                                    {member.user_id === group.owner_id && (
                                        <span className="ml-2 text-xs text-blue-500 font-medium">Owner</span>
                                    )}
                                </span>

                                {/* Remove button — owner can remove anyone except themselves */}
                                {isOwner && member.user_id !== user?.id && (
                                    <button
                                        onClick={() => handleRemoveMember(member.user_id)}
                                        className="text-xs text-red-500 hover:text-red-700"
                                    >
                                        Remove
                                    </button>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Sessions section */}
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-base font-semibold text-gray-900">Sessions</h3>

                        {/* Create session — owner only (spec: only the owner proposes slots) */}
                        {isOwner && (
                            <button
                                onClick={() => setShowSessionModal(true)}
                                className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                            >
                                + Propose Session
                            </button>
                        )}
                    </div>

                    {sessions.length === 0 ? (
                        <p className="text-sm text-gray-400">No sessions yet.</p>
                    ) : (
                        <div className="flex flex-col gap-4">
                            {sessions.map(session => (
                                <SessionCard
                                    key={session.id}
                                    session={session}
                                    isOwner={isOwner}
                                    isMember={isMember}
                                    justVotedSlotId={justVotedSlotId}
                                    onVote={slotId => handleVote(session.id, slotId)}
                                    onConfirm={slotId => handleConfirm(session.id, slotId)}
                                    onCancel={() => handleCancel(session.id)}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Create session modal */}
            {showSessionModal && (
                <CreateSessionModal
                    groupId={id}
                    onCreated={fetchAll}
                    onClose={() => setShowSessionModal(false)}
                />
            )}

            {/* Edit group modal */}
            {showEditModal && group && (
                <EditGroupModal
                    groupId={id}
                    currentName={group.name}
                    currentMaxSize={group.max_size}
                    currentMemberCount={group.members.length}
                    onUpdated={() => fetchAll(false)}
                    onClose={() => setShowEditModal(false)}
                />
            )}
        </div>
    )
}

// SessionCard sub-component

// Backend sends slot_date ("2026-09-20") + start_time ("14:30:00") + duration_minutes
// separately, with no end_time. Combine them into a readable "date, start - end" string.
// Voting stays open only while status is 'voting' AND the 24h deadline
// hasn't passed yet — the backend enforces the same check on the vote
// endpoint, this just keeps the button from being offered when it would
// only error.
function isVotingOpen(session: Session): boolean {
    return session.status === 'voting' && new Date(session.voting_deadline) > new Date()
}

function formatSlotRange(slot: Slot): string {
    const start = new Date(`${slot.slot_date}T${slot.start_time}`)
    const end = new Date(start.getTime() + slot.duration_minutes * 60000)
    const dateLabel = start.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
    const startLabel = start.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
    const endLabel = end.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
    return `${dateLabel}, ${startLabel} \u2013 ${endLabel}`
}

interface SessionCardProps {
    session: Session
    isOwner: boolean
    isMember: boolean
    justVotedSlotId: string | null
    onVote: (slotId: string) => void
    onConfirm: (slotId: string) => void
    onCancel: () => void
}

function SessionCard({ session, isOwner, isMember, justVotedSlotId, onVote, onConfirm, onCancel }: SessionCardProps) {

    // Status badge colour
    const statusColour =
        session.status === 'scheduled' ? 'bg-green-100 text-green-700' :
        session.status === 'completed' ? 'bg-blue-100 text-blue-700' :
        session.status === 'cancelled' ? 'bg-red-100 text-red-700' :
        'bg-yellow-100 text-yellow-700'  // voting

    return (
        <div className="rounded-xl border border-gray-100 bg-gray-50 p-4">

            {/* Session header */}
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-gray-900">{session.name}</h4>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColour}`}>
                        {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                    </span>
                </div>

                {/* Cancel button — owner only, allowed while voting or scheduled
                    (backend blocks it only once completed/cancelled) */}
                {isOwner && (session.status === 'voting' || session.status === 'scheduled') && (
                    <button
                        onClick={onCancel}
                        className="text-xs text-red-500 hover:text-red-700"
                    >
                        Cancel Session
                    </button>
                )}
            </div>

            {/* Slots */}
            <div className="flex flex-col gap-2">
                {session.slots.map(slot => {
                    // Check if this slot is the confirmed one
                    const isConfirmed = slot.id === session.confirmed_slot_id
                    const justVoted = slot.id === justVotedSlotId

                    return (
                        <div
                            key={slot.id}
                            className={`flex flex-col rounded-lg border px-3 py-2 transition-colors duration-500 ${
                                justVoted
                                    ? 'border-blue-400 bg-blue-50'
                                    : isConfirmed
                                    ? 'border-green-300 bg-green-50'
                                    : slot.voted_by_me
                                    ? 'border-blue-200 bg-blue-50/60'
                                    : 'border-gray-200 bg-white'
                            }`}
                        >
                        <div className="flex items-center justify-between">
                            {/* Slot time range */}
                            <div className="text-sm text-gray-800">
                                <span>{formatSlotRange(slot)}</span>
                                {slot.location && (
                                    <span className="ml-2 text-xs text-gray-400">· {slot.location}</span>
                                )}
                                {isConfirmed && (
                                    <span className="ml-2 text-xs text-green-600 font-medium">✓ Confirmed</span>
                                )}
                            </div>

                            {/* Vote count + action buttons — vote_count is null for
                                non-owners (owner-only visibility), so just omit it for them */}
                            <div className="flex items-center gap-3 ml-4 shrink-0">
                                {slot.vote_count !== null && (
                                    <span className="text-xs text-gray-500">{slot.vote_count} vote{slot.vote_count !== 1 ? 's' : ''}</span>
                                )}

                                {/* Vote — members only, while the 24h voting window is still open.
                                    Already-voted slots show "Voted" in blue but stay clickable, since the
                                    spec allows changing a vote any time before the deadline. */}
                                {isMember && isVotingOpen(session) && (
                                    <button
                                        onClick={() => onVote(slot.id)}
                                        className={`rounded-lg border px-2.5 py-1 text-xs ${
                                            slot.voted_by_me
                                                ? 'border-blue-400 bg-blue-100 text-blue-700 font-medium'
                                                : 'border-blue-300 text-blue-600 hover:bg-blue-50'
                                        }`}
                                    >
                                        {slot.voted_by_me ? 'Voted' : 'Vote'}
                                    </button>
                                )}
                                {/* Deadline passed but owner hasn't confirmed/cancelled yet —
                                    status is still 'voting', so make that state visible */}
                                {isMember && session.status === 'voting' && !isVotingOpen(session) && (
                                    <span className="text-xs text-gray-400 italic">Voting closed</span>
                                )}

                                {/* Confirm — owner only, while voting is open */}
                                {isOwner && session.status === 'voting' && (
                                    <button
                                        onClick={() => onConfirm(slot.id)}
                                        className="rounded-lg border border-green-300 px-2.5 py-1 text-xs text-green-600 hover:bg-green-50"
                                    >
                                        Confirm
                                    </button>
                                )}
                            </div>
                        </div>
                        {/* Transient confirmation shown for a few seconds right after voting */}
                        {justVoted && (
                            <p className="mt-1 text-xs text-blue-600 font-medium">
                                Vote has been recorded. You can change it anytime before the deadline.
                            </p>
                        )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
