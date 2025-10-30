// Piattaforma - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts dopo 5 secondi
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Conferma eliminazione
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Sei sicuro di voler eliminare questo elemento?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Highlight navigation attiva
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Popover initialization
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Utility: Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('it-IT', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('it-IT').format(date);
}

// Utility: Show loading spinner
function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'global-spinner';
    document.body.appendChild(spinner);
}

// Utility: Hide loading spinner
function hideLoading() {
    const spinner = document.getElementById('global-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Utility: Show toast notification (future implementation)
function showToast(message, type = 'info') {
    // TODO: Implementare toast notifications
    console.log(`[${type}] ${message}`);
}

// =============================================================================
// SESSION MANAGEMENT: Auto-save & Keep-Alive
// =============================================================================

// Keep-Alive: Ping server ogni 30 minuti per mantenere sessione attiva
function startSessionKeepAlive() {
    // Ping immediato dopo 29 minuti, poi ogni 30 minuti
    setInterval(() => {
        fetch('/api/ping', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).then(response => {
            if (response.ok) {
                console.log('[Session] Keep-alive ping successful');
            } else if (response.status === 401) {
                console.warn('[Session] Session expired, redirecting to login...');
                window.location.href = '/login';
            }
        }).catch(err => {
            console.error('[Session] Keep-alive ping failed:', err);
        });
    }, 30 * 60 * 1000); // 30 minuti
}

// Auto-save: Salva form in localStorage ogni 5 minuti
function startAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');

    forms.forEach(form => {
        const formId = form.getAttribute('data-autosave') || form.id || 'default-form';
        const storageKey = `autosave_${formId}`;

        // Recupera dati salvati all'avvio
        const savedData = localStorage.getItem(storageKey);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                const shouldRestore = confirm('Trovati dati non salvati. Vuoi recuperarli?');

                if (shouldRestore) {
                    Object.keys(data).forEach(name => {
                        const input = form.querySelector(`[name="${name}"]`);
                        if (input) {
                            input.value = data[name];
                        }
                    });
                    console.log(`[AutoSave] Restored data for form: ${formId}`);
                } else {
                    localStorage.removeItem(storageKey);
                }
            } catch (e) {
                console.error('[AutoSave] Error restoring data:', e);
            }
        }

        // Salva automaticamente ogni 5 minuti
        setInterval(() => {
            const formData = {};
            const inputs = form.querySelectorAll('input, select, textarea');

            inputs.forEach(input => {
                if (input.name && input.value) {
                    formData[input.name] = input.value;
                }
            });

            if (Object.keys(formData).length > 0) {
                localStorage.setItem(storageKey, JSON.stringify(formData));
                console.log(`[AutoSave] Saved form data: ${formId}`, formData);
            }
        }, 5 * 60 * 1000); // 5 minuti

        // Rimuovi autosave dopo submit riuscito
        form.addEventListener('submit', function() {
            setTimeout(() => {
                localStorage.removeItem(storageKey);
                console.log(`[AutoSave] Cleared saved data for: ${formId}`);
            }, 1000);
        });
    });
}

// Avvia keep-alive e auto-save quando il DOM è pronto
document.addEventListener('DOMContentLoaded', function() {
    // Avvia solo se l'utente è loggato (controlla se esiste elemento con user info)
    if (document.querySelector('.navbar-text') || document.body.classList.contains('logged-in')) {
        console.log('[Session] Starting keep-alive and auto-save...');
        startSessionKeepAlive();
        startAutoSave();
    }
});

// Export utilities
window.PiattaformaUtils = {
    formatCurrency,
    formatDate,
    showLoading,
    hideLoading,
    showToast,
    startSessionKeepAlive,
    startAutoSave
};
