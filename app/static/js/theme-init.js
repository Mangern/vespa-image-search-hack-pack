(function() {
    function getInitialTheme() {
        const persistedTheme = localStorage.getItem('theme');
        if (persistedTheme) return persistedTheme;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // Apply initial theme without transitions
    document.documentElement.classList.add('theme-transition-disabled');
    document.documentElement.classList.toggle('dark', getInitialTheme() === 'dark');

    // Remove the class after initial render
    window.addEventListener('load', () => {
        requestAnimationFrame(() => {
            document.documentElement.classList.remove('theme-transition-disabled');
        });
    });
})();