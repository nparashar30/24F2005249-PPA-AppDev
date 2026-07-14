const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            currentView: 'landing',
            user: null,
            profile: null,
            token: localStorage.getItem('ppa_token'),
            loading: false,
            error: '',
            success: '',
            publicStats: null,
            toast: { show: false, message: '', type: 'primary' },
            loginForm: { email: '', password: '' },
            studentForm: {
                full_name: '', student_id: '', email: '', password: '',
                branch: '', year: null, cgpa: null, phone: '', skills: '',
            },
            companyForm: {
                company_name: '', email: '', password: '', industry: '',
                location: '', website: '', hr_contact: '', description: '',
            },
        };
    },

    computed: {
        isLoggedIn() {
            return !!this.token && !!this.user;
        },
        api() {
            return API;
        },
        navItems() {
            if (!this.user) return [];
            const items = {
                admin: [
                    { view: 'dashboard', label: 'Dashboard' },
                    { view: 'companies', label: 'Companies' },
                    { view: 'students', label: 'Students' },
                    { view: 'drives', label: 'Drives' },
                    { view: 'applications', label: 'Applications' },
                    { view: 'reports', label: 'Reports' },
                ],
                company: [
                    { view: 'dashboard', label: 'Dashboard' },
                    { view: 'profile', label: 'Profile' },
                    { view: 'drives', label: 'Drives' },
                    { view: 'applications', label: 'Applications' },
                ],
                student: [
                    { view: 'dashboard', label: 'Dashboard' },
                    { view: 'profile', label: 'Profile' },
                    { view: 'drives', label: 'Browse Drives' },
                    { view: 'applications', label: 'Applications' },
                    { view: 'history', label: 'History' },
                ],
            };
            return items[this.user.role] || [];
        },
    },

    methods: {
        showToast(message, type = 'primary') {
            this.toast = { show: true, message, type };
            setTimeout(() => { this.toast.show = false; }, 3000);
        },

        async login() {
            this.loading = true;
            this.error = '';
            try {
                const res = await API.login(this.loginForm.email, this.loginForm.password);
                this.token = res.token;
                this.user = res.user;
                this.profile = res.profile;
                localStorage.setItem('ppa_token', res.token);
                this.currentView = 'dashboard';
                this.showToast('Login successful!', 'success');
            } catch (e) {
                this.error = e.message;
            } finally {
                this.loading = false;
            }
        },

        async registerStudent() {
            this.loading = true;
            this.error = '';
            try {
                const res = await API.registerStudent(this.studentForm);
                this.token = res.token;
                this.user = res.user;
                this.profile = res.profile;
                localStorage.setItem('ppa_token', res.token);
                this.currentView = 'dashboard';
                this.showToast('Registration successful!', 'success');
            } catch (e) {
                this.error = e.message;
            } finally {
                this.loading = false;
            }
        },

        async registerCompany() {
            this.loading = true;
            this.error = '';
            this.success = '';
            try {
                const res = await API.registerCompany(this.companyForm);
                this.success = res.message;
                this.showToast(res.message, 'success');
                setTimeout(() => { this.currentView = 'login'; }, 2000);
            } catch (e) {
                this.error = e.message;
            } finally {
                this.loading = false;
            }
        },

        logout() {
            this.token = null;
            this.user = null;
            this.profile = null;
            localStorage.removeItem('ppa_token');
            this.currentView = 'landing';
            this.showToast('Logged out', 'info');
        },

        goHome() {
            this.currentView = 'dashboard';
        },

        onProfileUpdated(profile) {
            this.profile = profile;
            this.showToast('Profile updated', 'success');
        },

        onApplied() {
            this.showToast('Application submitted!', 'success');
        },

        async restoreSession() {
            if (!this.token) return;
            try {
                const res = await API.me();
                this.user = res.user;
                this.profile = res.profile;
                this.currentView = 'dashboard';
            } catch {
                localStorage.removeItem('ppa_token');
                this.token = null;
            }
        },
    },

    async mounted() {
        try {
            this.publicStats = await API.publicStats();
        } catch (e) {
            console.warn('Could not load public stats');
        }
        await this.restoreSession();
    },
});

// Register components
app.component('admin-dashboard', AdminDashboard);
app.component('admin-companies', AdminCompanies);
app.component('admin-students', AdminStudents);
app.component('admin-drives', AdminDrives);
app.component('admin-applications', AdminApplications);
app.component('admin-reports', AdminReports);

app.component('company-dashboard', CompanyDashboard);
app.component('company-profile', CompanyProfile);
app.component('company-drives', CompanyDrives);
app.component('company-applications', CompanyApplications);

app.component('student-dashboard', StudentDashboard);
app.component('student-profile', StudentProfile);
app.component('student-drives', StudentDrives);
app.component('student-applications', StudentApplications);
app.component('student-history', StudentHistory);

app.mount('#app');
