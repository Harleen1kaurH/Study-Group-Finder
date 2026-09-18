'use client'

/**
 * EditGroupModal.tsx — modal for the owner to rename a group or change its
 * max size. Calls PUT /groups/{id} on submit.
 */

import { useState } from 'react'
import { updateGroup } from '../../lib/api'

interface Props {
    groupId: string
    currentName: string
    currentMaxSize: number
    currentMemberCount: number
    onUpdated: () => void
    onClose: () => void
}

export default function EditGroupModal({
    groupId,
    currentName,
    currentMaxSize,
    currentMemberCount,
    onUpdated,
    onClose,
}: Props) {
    const [name, setName] = useState(currentName)
    const [maxSize, setMaxSize] = useState(currentMaxSize)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            await updateGroup(groupId, { name, max_size: maxSize })
            onUpdated()
            onClose()
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to update group')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
            onClick={onClose}
        >
            <div
                className="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg"
                onClick={e => e.stopPropagation()}
            >
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Edit Group</h2>

                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    {/* Group name */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Group Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={e => setName(e.target.value)}
                            required
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

                    {/* Max size — can't drop below current member count */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Max Members</label>
                        <input
                            type="number"
                            min={Math.max(2, currentMemberCount)}
                            value={maxSize}
                            onChange={e => setMaxSize(Number(e.target.value))}
                            required
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                        <p className="text-xs text-gray-400">
                            Currently {currentMemberCount} member{currentMemberCount !== 1 ? 's' : ''} — can&apos;t go below that.
                        </p>
                    </div>

                    <div className="flex gap-3 mt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
