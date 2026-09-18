'use client'

/**
 * CreateGroupModal.tsx — modal form for creating a new study group.
 *
 * Takes course_code, name, and max_size, calls createGroup(),
 * then calls onCreated() to refresh the group list.
 */

import { useState } from 'react'
import { createGroup, createCourse } from '../lib/api'

interface Props {
    onCreated: () => void  // callback to refresh group list after creation
    onClose: () => void    // callback to close the modal
}

export default function CreateGroupModal({ onCreated, onClose }: Props) {
    const [name, setName] = useState('')
    const [courseCode, setCourseCode] = useState('')
    const [maxSize, setMaxSize] = useState(5)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // If the typed course code doesn't exist yet, we ask for its full name
    // so we can create it before creating the group.
    const [needsCourseName, setNeedsCourseName] = useState(false)
    const [courseName, setCourseName] = useState('')

    function handleCourseCodeChange(value: string) {
        // Course codes shouldn't contain spaces (e.g. "CS101", not "CS 101") —
        // strip any as the user types rather than rejecting on submit.
        const sanitized = value.replace(/\s/g, '')
        setCourseCode(sanitized)
        // Editing the code after we've flagged it as unknown resets that state,
        // since the new code might already exist.
        if (needsCourseName) {
            setNeedsCourseName(false)
            setCourseName('')
            setError(null)
        }
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            // If we already know this course code doesn't exist, create it first
            if (needsCourseName) {
                await createCourse({ code: courseCode, name: courseName })
            }
            await createGroup({ name, course_code: courseCode, max_size: maxSize })
            onCreated()  // refresh group list
            onClose()    // close modal
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Failed to create group'
            // Backend 404s with a message containing "not found" when the course
            // code doesn't exist — catch that and offer to create it instead of
            // just failing.
            if (!needsCourseName && message.toLowerCase().includes('not found')) {
                setNeedsCourseName(true)
                setError(`No course with code "${courseCode}" exists yet — enter its full name below to add it.`)
            } else {
                setError(message)
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        // Backdrop — clicking outside closes the modal
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
            onClick={onClose}
        >
            {/* Modal card — stop click from closing when clicking inside */}
            <div
                className="w-full max-w-md rounded-2xl bg-white p-6 shadow-lg"
                onClick={e => e.stopPropagation()}
            >
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Create a Study Group</h2>

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
                            placeholder="e.g. CS101 Morning Group"
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

                    {/* Course code */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Course Code</label>
                        <input
                            type="text"
                            value={courseCode}
                            onChange={e => handleCourseCodeChange(e.target.value)}
                            required
                            placeholder="e.g. CS101"
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

                    {/* Shown only after we've learned this course code doesn't exist yet */}
                    {needsCourseName && (
                        <div className="flex flex-col gap-1">
                            <label className="text-sm font-medium text-gray-700">Course Name</label>
                            <input
                                type="text"
                                value={courseName}
                                onChange={e => setCourseName(e.target.value)}
                                required
                                placeholder="e.g. Intro to Computer Science"
                                className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            />
                        </div>
                    )}

                    {/* Max size */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm font-medium text-gray-700">Max Members</label>
                        <input
                            type="number"
                            value={maxSize}
                            onChange={e => setMaxSize(Number(e.target.value))}
                            min={2}
                            required
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        />
                    </div>

                    <div className="flex gap-3 mt-2">
                        {/* Cancel button */}
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                        >
                            Cancel
                        </button>

                        {/* Submit button */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : needsCourseName ? 'Create Course & Group' : 'Create Group'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
