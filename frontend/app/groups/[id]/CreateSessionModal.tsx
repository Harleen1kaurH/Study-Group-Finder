'use client'

/**
 * CreateSessionModal.tsx — modal to propose a new study session.
 *
 * Owner proposes 2-4 candidate time slots (date, start time, duration,
 * optional location). The voting deadline is NOT chosen here — per spec,
 * the voting window is always exactly 24 hours from proposal time, so the
 * frontend computes it and sends it along with the slots.
 *
 * Calls POST /groups/{groupId}/sessions on submit.
 */

import { useState } from 'react'
import { createSession } from '../../lib/api'

interface SlotInput {
    slot_date: string        // "2026-09-20"
    start_time: string       // "14:30" from <input type="time">
    duration_minutes: number
    location: string
}

interface Props {
    groupId: string
    onCreated: () => void  // refresh sessions after creation
    onClose: () => void
}

function emptySlot(): SlotInput {
    return { slot_date: '', start_time: '', duration_minutes: 60, location: '' }
}

export default function CreateSessionModal({ groupId, onCreated, onClose }: Props) {
    // Spec requires 2-4 proposed slots — start at the minimum
    const [name, setName] = useState('')
    const [slots, setSlots] = useState<SlotInput[]>([emptySlot(), emptySlot()])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Update a specific slot field
    function updateSlot(index: number, field: keyof SlotInput, value: string | number) {
        setSlots(prev => prev.map((s, i) => i === index ? { ...s, [field]: value } : s))
    }

    // Add another slot row (max 4 per spec)
    function addSlot() {
        if (slots.length >= 4) return
        setSlots(prev => [...prev, emptySlot()])
    }

    // Remove a slot row (min 2 per spec)
    function removeSlot(index: number) {
        if (slots.length <= 2) return
        setSlots(prev => prev.filter((_, i) => i !== index))
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            // Voting window is exactly 24h from proposal time (spec) — not user-chosen
            const voting_deadline = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()

            await createSession(groupId, {
                name: name.trim(),
                voting_deadline,
                slots: slots.map(s => ({
                    slot_date: s.slot_date,
                    // <input type="time"> gives "HH:MM" — backend wants "HH:MM:SS"
                    start_time: s.start_time.length === 5 ? `${s.start_time}:00` : s.start_time,
                    duration_minutes: s.duration_minutes,
                    location: s.location.trim() === '' ? null : s.location,
                })),
            })
            onCreated()
            onClose()
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to create session')
        } finally {
            setLoading(false)
        }
    }

    return (
        // Backdrop
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
            onClick={onClose}
        >
            <div
                className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-lg max-h-[90vh] overflow-y-auto"
                onClick={e => e.stopPropagation()}
            >
                <h2 className="text-lg font-semibold text-gray-900 mb-1">Propose a Session</h2>
                <p className="text-xs text-gray-500 mb-4">
                    Propose 2–4 time options. Voting closes automatically 24 hours after you submit.
                </p>

                {error && (
                    <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex flex-col gap-4">

                    {/* Session name */}
                    <div className="flex flex-col gap-1">
                        <label className="text-xs font-medium text-gray-600">Session name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={e => setName(e.target.value)}
                            placeholder="e.g. Midterm Prep"
                            required
                            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500"
                        />
                    </div>

                    {/* Time slot rows */}
                    {slots.map((slot, i) => (
                        <div key={i} className="rounded-lg border border-gray-200 p-3 flex flex-col gap-2">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-medium text-gray-500">Slot {i + 1}</span>
                                {/* Remove button — only enabled above the 2-slot minimum */}
                                {slots.length > 2 && (
                                    <button
                                        type="button"
                                        onClick={() => removeSlot(i)}
                                        className="text-sm text-red-500 hover:text-red-700"
                                    >
                                        ✕
                                    </button>
                                )}
                            </div>

                            <div className="flex gap-2">
                                <div className="flex-1 flex flex-col gap-1">
                                    <label className="text-xs font-medium text-gray-600">Date</label>
                                    <input
                                        type="date"
                                        value={slot.slot_date}
                                        onChange={e => updateSlot(i, 'slot_date', e.target.value)}
                                        required
                                        className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500"
                                    />
                                </div>
                                <div className="flex-1 flex flex-col gap-1">
                                    <label className="text-xs font-medium text-gray-600">Start time</label>
                                    <input
                                        type="time"
                                        value={slot.start_time}
                                        onChange={e => updateSlot(i, 'start_time', e.target.value)}
                                        required
                                        className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500"
                                    />
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <div className="flex-1 flex flex-col gap-1">
                                    <label className="text-xs font-medium text-gray-600">Duration (minutes)</label>
                                    <input
                                        type="number"
                                        min={1}
                                        value={slot.duration_minutes}
                                        onChange={e => updateSlot(i, 'duration_minutes', Number(e.target.value))}
                                        required
                                        className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500"
                                    />
                                </div>
                                <div className="flex-1 flex flex-col gap-1">
                                    <label className="text-xs font-medium text-gray-600">Location / link (optional)</label>
                                    <input
                                        type="text"
                                        value={slot.location}
                                        onChange={e => updateSlot(i, 'location', e.target.value)}
                                        placeholder="e.g. Library room 3, or a Zoom link"
                                        className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-black outline-none focus:border-blue-500"
                                    />
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Add another slot — capped at 4 */}
                    {slots.length < 4 && (
                        <button
                            type="button"
                            onClick={addSlot}
                            className="text-sm text-blue-600 hover:underline text-left"
                        >
                            + Add another time slot
                        </button>
                    )}

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
                            {loading ? 'Proposing...' : 'Propose Session'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
