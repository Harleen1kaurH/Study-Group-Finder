// NEXT_PUBLIC_API_URL is set per-environment (Vercel project settings in
// production, .env.local for local dev) so the same code talks to the local
// FastAPI server in dev and the deployed backend in production.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Base fetch wrapper — credentials: 'include' sends the HttpOnly cookie automatically
// All API functions call this instead of fetch directly
async function request(path: string, options: RequestInit = {}) {
    const response = await fetch(`${BASE_URL}${path}`, {
        ...options,
        credentials: 'include',  // send the HttpOnly auth cookie with every request
        headers: {
            'Content-Type': 'application/json',
            // Allow caller to override headers if needed
            ...options.headers,
        },
    })

    // If the response is not 2xx, parse the error and throw it.
    // FastAPI sends detail as a plain string for our own HTTPExceptions, but
    // as a list of {loc, msg, type} objects for automatic validation errors
    // (422s) — handle both instead of assuming it's always a string.
    if (!response.ok) {
        const error = await response.json().catch(() => null)
        let message = 'Something went wrong'
        if (error) {
            if (typeof error.detail === 'string') {
                message = error.detail
            } else if (Array.isArray(error.detail)) {
                message = error.detail
                    .map((d: { msg?: string }) => d.msg)
                    .filter(Boolean)
                    .join('; ') || message
            }
        }
        throw new Error(message)
    }

    return response.json()
}

// Auth
export const register = (email: string, password: string, name: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name }) })

export const login = (email: string, password: string) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })

export const logout = () =>
    request('/auth/logout', { method: 'POST' })

// Users
export const getMe = () =>
    request('/users/me')

export const updateMe = (data: object) =>
    request('/users/me', { method: 'PUT', body: JSON.stringify(data) })

// Courses
export const getCourses = (code?: string) =>
    request(`/courses${code ? `?code=${code}` : ''}`)

export const createCourse = (data: object) =>
    request('/courses', { method: 'POST', body: JSON.stringify(data) })

// Groups
export const getGroups = (course_code?: string) =>
    request(`/groups${course_code ? `?course_code=${encodeURIComponent(course_code)}` : ''}`)

export const createGroup = (data: object) =>
    request('/groups', { method: 'POST', body: JSON.stringify(data) })

export const getGroup = (id: string) =>
    request(`/groups/${id}`)

export const updateGroup = (id: string, data: object) =>
    request(`/groups/${id}`, { method: 'PUT', body: JSON.stringify(data) })

export const deleteGroup = (id: string) =>
    request(`/groups/${id}`, { method: 'DELETE' })

export const joinGroup = (id: string) =>
    request(`/groups/${id}/join`, { method: 'POST' })

export const leaveGroup = (id: string) =>
    request(`/groups/${id}/leave`, { method: 'POST' })

export const removeMember = (groupId: string, userId: string) =>
    request(`/groups/${groupId}/members/${userId}`, { method: 'DELETE' })

// Sessions
export const getSessions = (groupId: string) =>
    request(`/groups/${groupId}/sessions`)

export const createSession = (groupId: string, data: object) =>
    request(`/groups/${groupId}/sessions`, { method: 'POST', body: JSON.stringify(data) })

export const getSession = (groupId: string, sessionId: string) =>
    request(`/groups/${groupId}/sessions/${sessionId}`)

export const voteOnSlot = (groupId: string, sessionId: string, slot_id: string) =>
    request(`/groups/${groupId}/sessions/${sessionId}/vote`, {
        method: 'POST',
        body: JSON.stringify({ slot_id }),
    })

export const confirmSlot = (groupId: string, sessionId: string, slot_id: string) =>
    request(`/groups/${groupId}/sessions/${sessionId}/confirm`, {
        method: 'POST',
        body: JSON.stringify({ slot_id }),
    })

export const cancelSession = (groupId: string, sessionId: string) =>
    request(`/groups/${groupId}/sessions/${sessionId}/cancel`, { method: 'POST' })

// Notifications
export const getNotifications = () =>
    request('/notifications')

// Upcoming sessions (dashboard box)
export const getUpcomingSessions = () =>
    request('/users/me/upcoming-sessions')
