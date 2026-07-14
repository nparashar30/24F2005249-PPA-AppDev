// Shared utility functions for Vue components

const statusBadge = (status) => {
    const map = {
        applied: 'secondary',
        shortlisted: 'info',
        interview: 'warning',
        offer: 'warning',
        selected: 'success',
        placed: 'success',
        rejected: 'danger',
        pending: 'secondary',
        approved: 'success',
        active: 'primary',
        closed: 'dark',
    };
    return map[status] || 'secondary';
};
