const BASE_URL = 'http://localhost:8000'

// Read the JWT token from localStorage
function getToken(): string | null {
    return localStorage.getItem('token')
}

// Base fetch wrapper — attaches auth header if token exists
// All API functions call this instead of fetch directly
async function request(path: string, options: RequestInit = {}) {
    const token = getToken()

    const response = await fetch(`${BASE_URL}${path}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            // Only add Authorization header if token exists
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            // Allow caller to override headers if needed
            ...options.headers,
        },
    })

    // If the response is not 2xx, parse the error and throw it
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Something went wrong')
    }

    return response.json()
}

// --- Auth ---
export const register = (email: string, password: string, name: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name }) })

export const login = (email: string, password: string) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })

export const logout = () =>
    request('/auth/logout', { method: 'POST' })

// --- Users ---
export const getMe = () =>
    request('/users/me')

export const updateMe = (data: object) =>
    request('/users/me', { method: 'PUT', body: JSON.stringify(data) })

// --- Courses ---
export const getCourses = (code?: string) =>
    request(`/courses${code ? `?code=${code}` : ''}`)

export const createCourse = (data: object) =>
    request('/courses', { method: 'POST', body: JSON.stringify(data) })

// --- Groups ---
export const getGroups = (course_id?: string) =>
    request(`/groups${course_id ? `?course_id=${course_id}` : ''}`)

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

// --- Sessions ---
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

// --- Notifications ---
export const getNotifications = () =>
    request('/notifications')
