
const API_BASE = '/api';

function getAuthHeaders() {
    const token = localStorage.getItem('tc_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

const api = {
    async register(name, email, password, role = 'Абитуриент') {
        const resp = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, role })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Registration failed');
        return data;
    },

    async login(email, password) {
        const resp = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Login failed');
        return data;
    },

    async getMe() {
        const token = localStorage.getItem('tc_token');
        const user = window.tcAuth ? window.tcAuth.getCurrentUser() : null;
        const email = user ? user.email : '';
        const resp = await fetch(`${API_BASE}/auth/me?email=${encodeURIComponent(email)}`, {
            headers: getAuthHeaders()
        });
        if (!resp.ok) return { authenticated: false, user: null };
        return await resp.json();
    },

    async getCredits() {
        const resp = await fetch(`${API_BASE}/user/credits`, {
            headers: getAuthHeaders()
        });
        if (!resp.ok) throw new Error('Failed to fetch credits');
        return await resp.json();
    },

    async deductCredit() {
        const resp = await fetch(`${API_BASE}/user/credits/deduct`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Credit deduction failed');
        return data;
    },

    async topUp(package_id, credits, amount_kzt = 0) {
        const resp = await fetch(`${API_BASE}/user/credits/topup`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ package_id, credits, amount_kzt })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Top-up failed');
        return data;
    },

    async applyPromo(code) {
        const resp = await fetch(`${API_BASE}/user/credits/promo`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ code })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Failed to apply promo');
        return data;
    },

    async suggest(query) {
        const resp = await fetch(`${API_BASE}/suggest?q=${encodeURIComponent(query)}`);
        if (!resp.ok) return null;
        return await resp.json();
    },

    async disambiguate(query) {
        const resp = await fetch(`${API_BASE}/disambiguate?q=${encodeURIComponent(query)}`);
        if (!resp.ok) return null;
        return await resp.json();
    },

    async analyze(query, agency_name = null, contact_email = null) {
        const token = localStorage.getItem('tc_token');
        const user = window.tcAuth ? window.tcAuth.getCurrentUser() : null;
        const user_email = user ? user.email : null;

        const resp = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                query,
                agency_name,
                contact_email,
                user_email,
                token
            })
        });
        const data = await resp.json();
        if (!resp.ok) {
            const err = new Error(data.detail || `Server error: ${resp.status}`);
            err.status = resp.status;
            err.detail = data.detail;
            throw err;
        }
        return data;
    },

    async compare(query1, query2) {
        const resp = await fetch(`${API_BASE}/compare`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ query1, query2 })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Comparison failed');
        return data;
    }
};

window.tcApi = api;
