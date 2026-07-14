// Admin Dashboard
const AdminDashboard = {
    props: ['api'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-speedometer2 me-2"></i>Admin Dashboard</h2>
        <div class="row g-3 mb-4" v-if="stats">
            <div class="col-md-3" v-for="(val, key) in statCards" :key="key">
                <div class="card dashboard-stat shadow-sm">
                    <div class="card-body text-center">
                        <h2 class="text-primary">{{ val }}</h2>
                        <p class="text-muted mb-0">{{ key }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    </div>`,
    data() { return { stats: null, loading: true }; },
    computed: {
        statCards() {
            if (!this.stats) return {};
            return {
                'Total Students': this.stats.total_students,
                'Approved Companies': this.stats.total_companies,
                'Pending Companies': this.stats.pending_companies,
                'Total Drives': this.stats.total_drives,
                'Active Drives': this.stats.approved_drives,
                'Pending Drives': this.stats.pending_drives,
                'Applications': this.stats.total_applications,
                'Placements': this.stats.total_placements,
            };
        }
    },
    async mounted() {
        try { this.stats = await this.api.adminDashboard(); }
        catch (e) { console.error(e); }
        finally { this.loading = false; }
    }
};

const AdminCompanies = {
    props: ['api'],
    template: `
    <div>
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-building me-2"></i>Companies</h2>
            <input type="search" class="form-control search-bar" placeholder="Search companies..." v-model="search" @input="load">
        </div>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Name</th><th>Industry</th><th>Location</th><th>Status</th><th>Actions</th>
                </tr></thead>
                <tbody>
                    <tr v-for="c in companies" :key="c.id">
                        <td>{{ c.company_name }}</td>
                        <td>{{ c.industry }}</td>
                        <td>{{ c.location }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(c.approval_status)">{{ c.approval_status }}</span></td>
                        <td>
                            <button v-if="c.approval_status==='pending'" class="btn btn-sm btn-success me-1" @click="approve(c.id,'approve')">Approve</button>
                            <button v-if="c.approval_status==='pending'" class="btn btn-sm btn-danger me-1" @click="approve(c.id,'reject')">Reject</button>
                            <button v-if="!c.is_active" class="btn btn-sm btn-outline-success me-1" @click="reactivate(c.id)">Reactivate</button>
                            <button v-if="c.is_active" class="btn btn-sm btn-outline-danger" @click="deactivate(c.id)">Deactivate</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { companies: [], search: '' }; },
    methods: {
        statusBadge,
        async load() {
            const q = this.search ? `?search=${encodeURIComponent(this.search)}` : '';
            this.companies = await this.api.adminCompanies(q);
        },
        async approve(id, action) {
            await this.api.approveCompany(id, action);
            await this.load();
        },
        async deactivate(id) {
            if (confirm('Deactivate this company?')) {
                await this.api.deactivateCompany(id, true);
                await this.load();
            }
        },
        async reactivate(id) {
            if (confirm('Reactivate this company?')) {
                await this.api.reactivateCompany(id);
                await this.load();
            }
        }
    },
    mounted() { this.load(); }
};

const AdminStudents = {
    props: ['api'],
    template: `
    <div>
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-people me-2"></i>Students</h2>
            <input type="search" class="form-control search-bar" placeholder="Search by name, ID, email..." v-model="search" @input="load">
        </div>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Student ID</th><th>Name</th><th>Branch</th><th>CGPA</th><th>Year</th><th>Status</th><th>Actions</th>
                </tr></thead>
                <tbody>
                    <tr v-for="s in students" :key="s.id">
                        <td>{{ s.student_id }}</td>
                        <td>{{ s.full_name }}</td>
                        <td>{{ s.branch }}</td>
                        <td>{{ s.cgpa }}</td>
                        <td>{{ s.year }}</td>
                        <td><span class="badge" :class="s.is_active ? 'bg-success' : 'bg-danger'">{{ s.is_active ? 'Active' : 'Inactive' }}</span></td>
                        <td>
                            <button v-if="!s.is_active" class="btn btn-sm btn-outline-success me-1" @click="reactivate(s.id)">Reactivate</button>
                            <button v-if="s.is_active" class="btn btn-sm btn-outline-danger" @click="deactivate(s.id)">Deactivate</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { students: [], search: '' }; },
    methods: {
        async load() {
            const q = this.search ? `?search=${encodeURIComponent(this.search)}` : '';
            this.students = await this.api.adminStudents(q);
        },
        async deactivate(id) {
            if (confirm('Deactivate this student?')) {
                await this.api.deactivateStudent(id, true);
                await this.load();
            }
        },
        async reactivate(id) {
            if (confirm('Reactivate this student?')) {
                await this.api.reactivateStudent(id);
                await this.load();
            }
        }
    },
    mounted() { this.load(); }
};

const AdminDrives = {
    props: ['api'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-calendar-event me-2"></i>Placement Drives</h2>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Title</th><th>Company</th><th>Deadline</th><th>Status</th><th>Actions</th>
                </tr></thead>
                <tbody>
                    <tr v-for="d in drives" :key="d.id">
                        <td>{{ d.title }}</td>
                        <td>{{ d.company_name }}</td>
                        <td>{{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString() : 'N/A' }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(d.status)">{{ d.status }}</span></td>
                        <td>
                            <button v-if="d.status==='pending'" class="btn btn-sm btn-success me-1" @click="approve(d.id,'approve')">Approve</button>
                            <button v-if="d.status==='pending'" class="btn btn-sm btn-danger" @click="approve(d.id,'reject')">Reject</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { drives: [] }; },
    methods: {
        statusBadge,
        async load() { this.drives = await this.api.adminDrives(); },
        async approve(id, action) {
            await this.api.approveDrive(id, action);
            await this.load();
        }
    },
    mounted() { this.load(); }
};

const AdminApplications = {
    props: ['api'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-file-earmark-text me-2"></i>All Applications</h2>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Student</th><th>Drive</th><th>Company</th><th>Status</th><th>Date</th>
                </tr></thead>
                <tbody>
                    <tr v-for="a in apps" :key="a.id">
                        <td>{{ a.student?.full_name }}</td>
                        <td>{{ a.job_title }}</td>
                        <td>{{ a.company_name }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(a.status)">{{ a.status }}</span></td>
                        <td>{{ new Date(a.application_date).toLocaleDateString() }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { apps: [] }; },
    methods: { statusBadge },
    async mounted() { this.apps = await this.api.adminApplications(); }
};

const AdminReports = {
    props: ['api'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-bar-chart me-2"></i>Placement Reports</h2>
        <div class="row g-4" v-if="stats">
            <div class="col-md-6">
                <div class="card shadow-sm"><div class="card-header fw-bold">Applications by Status</div>
                    <div class="card-body">
                        <div v-for="(count, status) in stats.applications_by_status" :key="status" class="d-flex justify-content-between mb-2">
                            <span class="badge" :class="'bg-' + statusBadge(status)">{{ status }}</span>
                            <strong>{{ count }}</strong>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card shadow-sm"><div class="card-header fw-bold">Placements by Company</div>
                    <div class="card-body">
                        <div v-for="(count, name) in stats.placements_by_company" :key="name" class="d-flex justify-content-between mb-2">
                            <span>{{ name }}</span><strong>{{ count }}</strong>
                        </div>
                        <p v-if="!Object.keys(stats.placements_by_company).length" class="text-muted">No placements yet</p>
                    </div>
                </div>
            </div>
        </div>
    </div>`,
    data() { return { stats: null }; },
    methods: { statusBadge },
    async mounted() { this.stats = await this.api.adminStats(); }
};
