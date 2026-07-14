const CompanyDashboard = {
    props: ['api', 'profile'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-speedometer2 me-2"></i>Company Dashboard</h2>
        <div v-if="profile?.approval_status !== 'approved'" class="alert alert-warning">
            Your company is pending admin approval. You cannot create drives until approved.
        </div>
        <div class="row g-3 mb-4" v-if="data">
            <div class="col-md-4"><div class="card dashboard-stat shadow-sm"><div class="card-body text-center">
                <h2 class="text-primary">{{ data.drives?.length || 0 }}</h2><p class="text-muted mb-0">Placement Drives</p>
            </div></div></div>
            <div class="col-md-4"><div class="card dashboard-stat shadow-sm"><div class="card-body text-center">
                <h2 class="text-success">{{ data.total_applications || 0 }}</h2><p class="text-muted mb-0">Total Applicants</p>
            </div></div></div>
            <div class="col-md-4"><div class="card dashboard-stat shadow-sm"><div class="card-body text-center">
                <h3 class="text-info">{{ data.company?.company_name }}</h3><p class="text-muted mb-0">Your Company</p>
            </div></div></div>
        </div>
        <h4 class="mb-3">Your Drives</h4>
        <div class="table-responsive card shadow-sm" v-if="data">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr><th>Title</th><th>Status</th><th>Applicants</th><th>Deadline</th></tr></thead>
                <tbody>
                    <tr v-for="d in data.drives" :key="d.id">
                        <td>{{ d.title }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(d.status)">{{ d.status }}</span></td>
                        <td>{{ d.applicant_count }}</td>
                        <td>{{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString() : 'N/A' }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() { return { data: null }; },
    methods: { statusBadge },
    async mounted() { this.data = await this.api.companyDashboard(); }
};

const CompanyProfile = {
    props: ['api', 'profile'],
    emits: ['updated'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-building me-2"></i>Company Profile</h2>
        <div class="card shadow-sm"><div class="card-body p-4">
            <form @submit.prevent="save">
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Company Name</label>
                        <input type="text" class="form-control" v-model="form.company_name" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Industry</label>
                        <input type="text" class="form-control" v-model="form.industry"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Location</label>
                        <input type="text" class="form-control" v-model="form.location"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Website</label>
                        <input type="url" class="form-control" v-model="form.website"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">HR Contact</label>
                        <input type="text" class="form-control" v-model="form.hr_contact"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">HR Email</label>
                        <input type="email" class="form-control" v-model="form.hr_email"></div>
                    <div class="col-12 mb-3"><label class="form-label">Description</label>
                        <textarea class="form-control" v-model="form.description" rows="3"></textarea></div>
                </div>
                <div v-if="msg" class="alert alert-success">{{ msg }}</div>
                <button type="submit" class="btn btn-primary">Save Profile</button>
            </form>
        </div></div>
    </div>`,
    data() { return { form: { ...this.profile }, msg: '' }; },
    methods: {
        async save() {
            const res = await this.api.updateCompanyProfile(this.form);
            this.msg = res.message;
            this.$emit('updated', res.company);
        }
    }
};

const CompanyDrives = {
    props: ['api'],
    template: `
    <div>
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-briefcase me-2"></i>Placement Drives</h2>
            <button class="btn btn-primary" @click="showForm = !showForm">
                <i class="bi bi-plus-lg me-1"></i>Create Drive
            </button>
        </div>
        <div v-if="showForm" class="card shadow-sm mb-4"><div class="card-body p-4">
            <h5>New Placement Drive</h5>
            <form @submit.prevent="create">
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Job Title *</label>
                        <input type="text" class="form-control" v-model="form.title" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Salary</label>
                        <input type="text" class="form-control" v-model="form.salary" placeholder="12 LPA"></div>
                    <div class="col-12 mb-3"><label class="form-label">Description</label>
                        <textarea class="form-control" v-model="form.description" rows="2"></textarea></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Skills Required</label>
                        <input type="text" class="form-control" v-model="form.skills_required"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Experience</label>
                        <input type="text" class="form-control" v-model="form.experience_required"></div>
                    <div class="col-md-4 mb-3"><label class="form-label">Eligible Branch</label>
                        <input type="text" class="form-control" v-model="form.eligibility_branch" placeholder="CSE, ECE"></div>
                    <div class="col-md-4 mb-3"><label class="form-label">Min CGPA</label>
                        <input type="number" step="0.1" class="form-control" v-model.number="form.eligibility_cgpa"></div>
                    <div class="col-md-4 mb-3"><label class="form-label">Eligible Year</label>
                        <input type="number" class="form-control" v-model.number="form.eligibility_year"></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Application Deadline</label>
                        <input type="datetime-local" class="form-control" v-model="form.application_deadline"></div>
                </div>
                <div v-if="error" class="alert alert-danger">{{ error }}</div>
                <button type="submit" class="btn btn-success">Submit for Approval</button>
            </form>
        </div></div>
        <div class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Title</th><th>Status</th><th>Deadline</th><th>Actions</th>
                </tr></thead>
                <tbody>
                    <tr v-for="d in drives" :key="d.id">
                        <td>{{ d.title }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(d.status)">{{ d.status }}</span></td>
                        <td>{{ d.application_deadline ? new Date(d.application_deadline).toLocaleDateString() : 'N/A' }}</td>
                        <td>
                            <button v-if="['approved','active'].includes(d.status)" class="btn btn-sm btn-warning me-1" @click="closeDrive(d.id)">Close</button>
                            <button v-if="d.status==='approved'" class="btn btn-sm btn-success" @click="activateDrive(d.id)">Activate</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>`,
    data() {
        return {
            drives: [], showForm: false, error: '',
            form: { title: '', description: '', skills_required: '', experience_required: '',
                    salary: '', eligibility_branch: '', eligibility_cgpa: null, eligibility_year: null,
                    application_deadline: '' }
        };
    },
    methods: {
        statusBadge,
        async load() { this.drives = await this.api.companyDrives(); },
        async create() {
            try {
                const data = { ...this.form };
                if (data.application_deadline) data.application_deadline = new Date(data.application_deadline).toISOString();
                await this.api.createDrive(data);
                this.showForm = false;
                this.form = { title: '', description: '', skills_required: '', experience_required: '',
                    salary: '', eligibility_branch: '', eligibility_cgpa: null, eligibility_year: null, application_deadline: '' };
                await this.load();
            } catch (e) { this.error = e.message; }
        },
        async closeDrive(id) { await this.api.updateDriveStatus(id, 'closed'); await this.load(); },
        async activateDrive(id) { await this.api.updateDriveStatus(id, 'active'); await this.load(); },
    },
    mounted() { this.load(); }
};

const CompanyApplications = {
    props: ['api'],
    template: `
    <div>
        <h2 class="mb-4"><i class="bi bi-people me-2"></i>Manage Applications</h2>
        <div class="mb-3">
            <select class="form-select" style="max-width:300px" v-model="selectedDrive" @change="loadApps">
                <option value="">Select a drive...</option>
                <option v-for="d in drives" :key="d.id" :value="d.id">{{ d.title }}</option>
            </select>
        </div>
        <div v-if="apps.length" class="table-responsive card shadow-sm">
            <table class="table table-hover mb-0">
                <thead class="table-light"><tr>
                    <th>Student</th><th>Branch</th><th>CGPA</th><th>Status</th><th>Actions</th>
                </tr></thead>
                <tbody>
                    <tr v-for="a in apps" :key="a.id">
                        <td>{{ a.student?.full_name }}</td>
                        <td>{{ a.student?.branch }}</td>
                        <td>{{ a.student?.cgpa }}</td>
                        <td><span class="badge" :class="'bg-' + statusBadge(a.status)">{{ a.status }}</span></td>
                        <td>
                            <select class="form-select form-select-sm" style="width:auto;display:inline-block"
                                    :value="a.status" @change="updateStatus(a.id, $event.target.value)">
                                <option value="applied">Applied</option>
                                <option value="shortlisted">Shortlisted</option>
                                <option value="interview">Interview</option>
                                <option value="offer">Offer</option>
                                <option value="selected">Selected</option>
                                <option value="rejected">Rejected</option>
                                <option value="placed">Placed</option>
                            </select>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p v-else-if="selectedDrive" class="text-muted">No applications for this drive.</p>
    </div>`,
    data() { return { drives: [], selectedDrive: '', apps: [] }; },
    methods: {
        statusBadge,
        async load() { this.drives = await this.api.companyDrives(); },
        async loadApps() {
            if (!this.selectedDrive) { this.apps = []; return; }
            this.apps = await this.api.driveApplications(this.selectedDrive);
        },
        async updateStatus(id, status) {
            await this.api.updateApplicationStatus(id, { status });
            await this.loadApps();
        }
    },
    mounted() { this.load(); }
};
