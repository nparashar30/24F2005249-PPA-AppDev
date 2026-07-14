const StudentDashboard = {
    props: ['api', 'profile'],
    template: `
    <div>
        <h2 class="mb-4">Welcome, {{ profile?.full_name }}!</h2>
        <div class="row g-3 mb-4" v-if="data">
            <div class="col-md-4"><div class="card dashboard-stat shadow-sm"><div class="card-body text-center">
                <h2 class="text-primary">{{ data.approved_drives?.length || 0 }}</h2>
                <p class="text-muted mb-0">Open Drives</p>
            </div></div></div>
            <div class="col-md-4"><div class="card dashboard-stat shadow-sm"><div class="card-body text-center">
                <h2 class="text-info">{{ data.recent_applications?.length || 0 }}</h2>
                <p class="text-muted mb-0">Recent Applications</p>
            </div></div></div>
            <div class="col-md-4"><div class="card dashboard-stat shadow-sm"><div class="card-body text-center">
                <h2 class="text-success">{{ data.placement_count || 0 }}</h2>
                <p class="text-muted mb-0">Placements</p>
            </div></div></div>
        </div>
        <h4 class="mb-3">Recent Applications</h4>
        <div class="table-responsive card shadow-sm" v-if="data?.recent_applications?.length">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Drive</th><th>Company</th><th>Status</th><th>Date</th></tr></thead>
                <tbody>
                    <tr v-for="a in data.recent_applications" :key="a.id">
                        <td>{{ a.job_title }}</td>
                        <td>{{ a.company_name }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(a.status)">{{ a.status }}</span></td>
                        <td>{{ new Date(a.application_date).toLocaleDateString() }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p v-else class="text-muted">No applications yet. Browse drives to apply!</p>
    </div>`,
    data() { return { data: null }; },
    methods: { statusBadge },
    async mounted() { this.data = await this.api.studentDashboard(); }
};

const StudentProfile = {
    props: ['api', 'profile'],
    emits: ['updated'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-person me-2"></i>My Profile</h2>
        <div class="card shadow-sm"><div class="card-body p-4">
            <form @submit.prevent="save">
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Full Name</label>
                        <input type="text" class="form-control" v-model="form.full_name" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Student ID</label>
                        <input type="text" class="form-control" :value="form.student_id" disabled></div>
                    <div class="col-md-4 mb-3"><label class="form-label">Branch</label>
                        <input type="text" class="form-control" v-model="form.branch"></div>
                    <div class="col-md-4 mb-3"><label class="form-label">Year</label>
                        <input type="number" class="form-control" v-model.number="form.year"></div>
                    <div class="col-md-4 mb-3"><label class="form-label">CGPA</label>
                        <input type="number" step="0.01" class="form-control" v-model.number="form.cgpa"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Phone</label>
                        <input type="tel" class="form-control" v-model="form.phone"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Skills</label>
                        <input type="text" class="form-control" v-model="form.skills"></div>
                    <div class="col-12 mb-3"><label class="form-label">Education</label>
                        <textarea class="form-control" v-model="form.education" rows="2"></textarea></div>
                    <div class="col-12 mb-3"><label class="form-label">Experience</label>
                        <textarea class="form-control" v-model="form.experience" rows="2"></textarea></div>
                    <div class="col-12 mb-3">
                        <label class="form-label">Resume</label>
                        <input type="file" class="form-control" accept=".pdf,.doc,.docx" @change="onFile">
                        <small v-if="form.resume_path" class="text-muted">Current: {{ form.resume_path }}</small>
                    </div>
                </div>
                <div v-if="msg" class="alert alert-success">{{ msg }}</div>
                <button type="submit" class="btn btn-primary">Save Profile</button>
            </form>
        </div></div>
    </div>`,
    data() { return { form: { ...this.profile }, msg: '', resumeFile: null }; },
    methods: {
        onFile(e) { this.resumeFile = e.target.files[0]; },
        async save() {
            const res = await this.api.updateStudentProfile(this.form);
            if (this.resumeFile) {
                const fd = new FormData();
                fd.append('resume', this.resumeFile);
                await this.api.uploadResume(fd);
            }
            this.msg = res.message;
            this.$emit('updated', res.student);
        }
    }
};

const StudentDrives = {
    props: ['api'],
    emits: ['applied'],
    template: `
    <div>
        <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
            <h2><i class="bi bi-search me-2"></i>Browse Drives</h2>
            <div class="d-flex gap-2">
                <input type="search" class="form-control" placeholder="Search drives..." v-model="search" @input="load">
                <input type="search" class="form-control" placeholder="Company..." v-model="company" @input="load">
            </div>
        </div>
        <div class="row g-3">
            <div class="col-md-6 col-lg-4" v-for="d in drives" :key="d.id">
                <div class="card shadow-sm h-100">
                    <div class="card-body">
                        <h5 class="card-title">{{ d.title }}</h5>
                        <h6 class="card-subtitle text-muted mb-2">{{ d.company_name }}</h6>
                        <p class="card-text small">{{ d.description?.substring(0, 100) }}...</p>
                        <div class="mb-2">
                            <span v-if="d.salary" class="badge bg-success me-1">{{ d.salary }}</span>
                            <span v-if="d.eligibility_cgpa" class="badge bg-info me-1">CGPA ≥ {{ d.eligibility_cgpa }}</span>
                            <span v-if="d.eligibility_branch" class="badge bg-secondary">{{ d.eligibility_branch }}</span>
                        </div>
                        <p class="small text-muted mb-2" v-if="d.application_deadline">
                            Deadline: {{ new Date(d.application_deadline).toLocaleDateString() }}
                        </p>
                        <button v-if="!d.already_applied && d.eligible" class="btn btn-primary btn-sm"
                                @click="apply(d.id)" :disabled="applying">Apply Now</button>
                        <span v-else-if="d.already_applied" class="badge bg-success">Applied</span>
                        <span v-else class="badge bg-danger">{{ d.eligibility_reason }}</span>
                    </div>
                </div>
            </div>
        </div>
        <p v-if="!drives.length" class="text-muted text-center py-5">No drives available.</p>
    </div>`,
    data() { return { drives: [], search: '', company: '', applying: false }; },
    methods: {
        async load() {
            let q = '?nocache=1';
            if (this.search) q += `&search=${encodeURIComponent(this.search)}`;
            if (this.company) q += `&company=${encodeURIComponent(this.company)}`;
            this.drives = await this.api.studentDrives(q);
        },
        async apply(id) {
            this.applying = true;
            try {
                await this.api.applyDrive(id);
                this.$emit('applied');
                await this.load();
            } catch (e) { alert(e.message); }
            finally { this.applying = false; }
        }
    },
    mounted() { this.load(); }
};

const StudentApplications = {
    props: ['api'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-file-earmark-text me-2"></i>My Applications</h2>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Drive</th><th>Company</th><th>Status</th><th>Applied</th><th>Interview</th><th>Feedback</th>
                </tr></thead>
                <tbody>
                    <tr v-for="a in apps" :key="a.id">
                        <td>{{ a.job_title }}</td>
                        <td>{{ a.company_name }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(a.status)">{{ a.status }}</span></td>
                        <td>{{ new Date(a.application_date).toLocaleDateString() }}</td>
                        <td>{{ a.interview_date ? new Date(a.interview_date).toLocaleString() : '-' }}</td>
                        <td>{{ a.feedback || '-' }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p v-if="!apps.length" class="text-muted">No applications yet.</p>
    </div>`,
    data() { return { apps: [] }; },
    methods: { statusBadge },
    async mounted() { this.apps = await this.api.studentApplications(); }
};

const StudentHistory = {
    props: ['api'],
    template: `
    <div>
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-clock-history me-2"></i>Placement History</h2>
            <button class="btn btn-outline-primary" @click="exportCsv" :disabled="exporting">
                <i class="bi bi-download me-1"></i>{{ exporting ? 'Exporting...' : 'Export CSV' }}
            </button>
        </div>
        <div v-if="exportMsg" class="alert alert-info">{{ exportMsg }}</div>
        <h4 class="mb-3">Placements</h4>
        <div class="table-responsive card shadow-sm mb-4" v-if="history?.placements?.length">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Company</th><th>Position</th><th>Salary</th><th>Date</th></tr></thead>
                <tbody>
                    <tr v-for="p in history.placements" :key="p.id">
                        <td>{{ p.company_name }}</td>
                        <td>{{ p.position }}</td>
                        <td>{{ p.salary }}</td>
                        <td>{{ new Date(p.placed_at).toLocaleDateString() }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p v-else class="text-muted mb-4">No placements yet.</p>
        <h4 class="mb-3">All Applications</h4>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Drive</th><th>Company</th><th>Status</th><th>Date</th></tr></thead>
                <tbody>
                    <tr v-for="a in history?.applications" :key="a.id">
                        <td>{{ a.job_title }}</td>
                        <td>{{ a.company_name }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(a.status)">{{ a.status }}</span></td>
                        <td>{{ new Date(a.application_date).toLocaleDateString() }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { history: null, exporting: false, exportMsg: '' }; },
    methods: {
        statusBadge,
        async exportCsv() {
            this.exporting = true;
            try {
                const res = await this.api.exportCsv();
                this.exportMsg = res.message + ' Task ID: ' + res.task_id;
            } catch (e) { this.exportMsg = e.message; }
            finally { this.exporting = false; }
        }
    },
    async mounted() { this.history = await this.api.studentHistory(); }
};
