// User behavior tracking
class UserAnalytics {
    constructor() {
        this.pageStartTime = new Date();
        this.currentPage = window.location.pathname;
        this.setupPageTracking();
        this.setupUserInteractions();
    }

    setupPageTracking() {
        // Track page view
        this.trackPageView();

        // Track time spent on page
        window.addEventListener('beforeunload', () => {
            this.trackTimeSpent();
        });

        // Track page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.trackTimeSpent();
            } else if (document.visibilityState === 'visible') {
                this.pageStartTime = new Date();
            }
        });
    }

    setupUserInteractions() {
        // Track form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.trackFormSubmission(e.target);
            });
        });

        // Track button clicks
        document.querySelectorAll('button, .btn, [role="button"]').forEach(button => {
            button.addEventListener('click', (e) => {
                this.trackButtonClick(e.target);
            });
        });

        // Track link clicks
        document.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', (e) => {
                this.trackLinkClick(e.target);
            });
        });
    }

    trackPageView() {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_view', {
                'page_title': document.title,
                'page_location': window.location.href,
                'page_path': window.location.pathname,
                'user_id': this.getUserId(),
                'user_role': this.getUserRole()
            });
        }
    }

    trackTimeSpent() {
        const timeSpent = (new Date() - this.pageStartTime) / 1000; // in seconds
        if (typeof gtag !== 'undefined' && timeSpent > 0) {
            gtag('event', 'time_spent', {
                'page_path': this.currentPage,
                'time_spent_seconds': Math.round(timeSpent),
                'user_id': this.getUserId(),
                'user_role': this.getUserRole()
            });
        }
    }

    trackFormSubmission(form) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'form_submission', {
                'form_id': form.id || 'unnamed_form',
                'form_action': form.action,
                'page_path': this.currentPage,
                'user_id': this.getUserId(),
                'user_role': this.getUserRole()
            });
        }
    }

    trackButtonClick(button) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'button_click', {
                'button_id': button.id || 'unnamed_button',
                'button_text': button.textContent.trim(),
                'page_path': this.currentPage,
                'user_id': this.getUserId(),
                'user_role': this.getUserRole()
            });
        }
    }

    trackLinkClick(link) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'link_click', {
                'link_url': link.href,
                'link_text': link.textContent.trim(),
                'page_path': this.currentPage,
                'user_id': this.getUserId(),
                'user_role': this.getUserRole()
            });
        }
    }

    getUserId() {
        return document.body.getAttribute('data-user-id') || '';
    }

    getUserRole() {
        return document.body.getAttribute('data-user-role') || '';
    }
}

// Initialize user analytics when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.userAnalytics = new UserAnalytics();
}); 