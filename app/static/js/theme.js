// Immediately invoked function to set theme before page load
(function() {
    function getInitialTheme() {
        const persistedTheme = localStorage.getItem('theme');
        const hasPersistedPreference = typeof persistedTheme === 'string';

        if (hasPersistedPreference) {
            return persistedTheme;
        }

        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const hasMediaQueryPreference = typeof mediaQuery.matches === 'boolean';

        if (hasMediaQueryPreference) {
            return mediaQuery.matches ? 'dark' : 'light';
        }

        return 'light';
    }

    const theme = getInitialTheme();
    document.documentElement.classList.toggle('dark', theme === 'dark');
})();

const themeManager = {
    getPreferredTheme() {
        return localStorage.theme === 'dark' ||
        (!('theme' in localStorage) &&
            window.matchMedia('(prefers-color-scheme: dark)').matches)
            ? 'dark'
            : 'light';
    },

    setTheme(theme) {
        // Store the currently focused element
        const focusedElement = document.activeElement;
        const focusedElementId = focusedElement?.id;

        localStorage.theme = theme;
        document.documentElement.classList.toggle('dark', theme === 'dark');
        window.dispatchEvent(new CustomEvent('theme-changed', {
            detail: { theme }
        }));

        // Restore focus after a brief delay to ensure DOM updates are complete
        if (focusedElementId) {
            requestAnimationFrame(() => {
                const elementToFocus = document.getElementById(focusedElementId);
                if (elementToFocus) {
                    elementToFocus.focus();
                    // If it's an input, preserve cursor position
                    if (elementToFocus.tagName === 'INPUT' && 'selectionStart' in focusedElement) {
                        const start = focusedElement.selectionStart;
                        const end = focusedElement.selectionEnd;
                        elementToFocus.setSelectionRange(start, end);
                    }
                }
            });
        }
    },

    toggle() {
        const newTheme = document.documentElement.classList.contains('dark')
            ? 'light'
            : 'dark';
        this.setTheme(newTheme);
    },

    init() {
        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', e => {
                if (!('theme' in localStorage)) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });

        // Watch for localStorage changes from other tabs
        window.addEventListener('storage', e => {
            if (e.key === 'theme') {
                this.setTheme(e.newValue);
            }
        });

        // Initialize click handlers for theme toggle buttons
        document.addEventListener('click', e => {
            if (e.target.closest('.theme-toggle')) {
                e.preventDefault();
                this.toggle();
            }
        });
    }
};

// Initialize theme system
themeManager.init();
