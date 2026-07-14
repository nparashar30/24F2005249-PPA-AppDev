const API = {
    base: '/api',

    async request(method, path, body = null, isForm = false) {
        const headers = {};
        const token = localStorage.getItem('ppa_token');
        if (token) headers['Authorization'] = `Bearer ${token}`;
        if (!isForm) headers['Content-Type'] = 'application/json';

        const opts = { method, headers };
        if (body) opts.body = isForm ? body : JSON.stringify(body);

        const res = await fetch(`${this.base}${path}`, opts);
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.error || data.errors?.join(', ') || 'Request failed');
        return data;
    },

    get(path) { return this.request('GET', path); },
    post(path, body) { return this.request('POST', path, body); },
    put(path, body) { return this.request('PUT', path, body); },

    // Auth
    login(email, password) { return this.post('/auth/login', { email, password }); },
    registerStudent(data) { return this.post('/auth/register/student', data); },
    registerCompany(data) { return this.post('/auth/register/company', data); },
    me() { return this.get('/auth/me'); },

    // Public
    publicStats() { return fetch('/api/public/stats').then(r => r.json()); },

    // Admin
    adminDashboard() { return this.get('/admin/dashboard'); },
    adminCompanies(params = '') { return this.get(`/admin/companies${params}`); },
    approveCompany(id, action) { return this.put(`/admin/companies/${id}/approve`, { action }); },
    deactivateCompany(id, blacklist) { return this.put(`/admin/companies/${id}/deactivate`, { blacklist }); },
    reactivateCompany(id) { return this.put(`/admin/companies/${id}/reactivate`); },
    adminStudents(params = '') { return this.get(`/admin/students${params}`); },
    deactivateStudent(id, blacklist) { return this.put(`/admin/students/${id}/deactivate`, { blacklist }); },
    reactivateStudent(id) { return this.put(`/admin/students/${id}/reactivate`); },
    adminDrives(params = '') { return this.get(`/admin/drives${params}`); },
    approveDrive(id, action) { return this.put(`/admin/drives/${id}/approve`, { action }); },
    adminApplications() { return this.get('/admin/applications'); },
    adminStats() { return this.get('/admin/reports/stats'); },

    // Company
    companyDashboard() { return this.get('/company/dashboard'); },
    companyProfile() { return this.get('/company/profile'); },
    updateCompanyProfile(data) { return this.put('/company/profile', data); },
    companyDrives(params = '') { return this.get(`/company/drives${params}`); },
    createDrive(data) { return this.post('/company/drives', data); },
    updateDriveStatus(id, status) { return this.put(`/company/drives/${id}/status`, { status }); },
    driveApplications(driveId) { return this.get(`/company/drives/${driveId}/applications`); },
    updateApplicationStatus(id, data) { return this.put(`/company/applications/${id}/status`, data); },

    // Student
    studentDashboard() { return this.get('/student/dashboard'); },
    studentProfile() { return this.get('/student/profile'); },
    updateStudentProfile(data) { return this.put('/student/profile', data); },
    uploadResume(formData) { return this.request('POST', '/student/profile/resume', formData, true); },
    studentDrives(params = '') { return this.get(`/student/drives${params}`); },
    applyDrive(id) { return this.post(`/student/drives/${id}/apply`); },
    studentApplications() { return this.get('/student/applications'); },
    studentPlacements() { return this.get('/student/placements'); },
    studentHistory() { return this.get('/student/history'); },
    exportCsv() { return this.post('/student/export/csv'); },
    exportStatus(taskId) { return this.get(`/student/export/status/${taskId}`); },
    downloadExport(filename) { return `/api/student/export/download/${filename}`; },
};
