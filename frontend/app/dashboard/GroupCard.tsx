'use client'

/**
 * GroupCard.tsx — displays a single study group in the dashboard list.
 *
 * Shows the group name, course, member count, and a join button if the
 * logged-in user is not already a member.
 */

import { useRouter } from 'next/navigation'
import { joinGroup } from '../lib/api'

interface Group {
    id: string
    name: string
    course_id: string
    owner_id: string
    max_size: number
    created_at: string
    is_member: boolean
}

interface Props {
    group: Group
    currentUserId: string
    onJoined: () => void  // callback to refresh the group list after joining
}

export default function GroupCard({ group, currentUserId, onJoined }: Props) {
    const router = useRouter()

    async function handleJoin(e: React.MouseEvent) {
        // Stop the click from bubbling up to the card (which navigates to group page)
        e.stopPropagation()
        try {
            await joinGroup(group.id)
            onJoined()
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Failed to join group')
        }
    }

    return (
        <div
            onClick={() => router.push(`/groups/${group.id}`)}
            className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
        >
            <div>
                {/* Group name */}
                <p className="font-semibold text-gray-900">{group.name}</p>
                {/* Max size */}
                <p className="text-sm text-gray-500">Max {group.max_size} members</p>
            </div>

            {/* Join button — only for users who are neither the owner nor already a member */}
            {group.owner_id !== currentUserId && !group.is_member && (
                <button
                    onClick={handleJoin}
                    className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
                >
                    Join
                </button>
            )}
        </div>
    )
}
