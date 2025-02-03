from fasthtml.common import Div, Form, Script, Style

from ...components.button import button
from ...components.container import container
from ...components.icon import icon
from ...components.text import text
from ...components.text_input import text_input

SEARCH_PROMPTS = [
    "Looking for something specific?",
    "Try 'sunset over mountains'",
    "Search for 'group of friends laughing'",
    "Find 'dog playing in snow'",
    "What would you like to find?",
]

SEARCH_STYLES = """
    #search-input {
        transition: all 0.3s ease-out;
    }

    #search-input.caption-filled {
        color: var(--low-contrast-text-green);
    }

    .enter-hint {
        opacity: 0;
        transform: translateX(10px);
        transition: all 0.2s ease-out;
    }

    .enter-hint.visible {
        opacity: 1;
        transform: translateX(0);
    }

    /* Hide loading button by default */
    .loading-btn {
        display: none;
    }

    /* Show loading button and hide search button during form submit */
    .submitting .search-btn {
        display: none;
    }

    .submitting .loading-btn {
        display: flex;
        opacity: 0.7;
    }
"""

SEARCH_SCRIPT = """
    const searchInput = document.getElementById('search-input');
    const enterHint = document.querySelector('.enter-hint');
    const form = document.querySelector('form');
    const prompts = ${search_prompts};

    // Always focus input on initial load
    searchInput.focus();

    // Re-focus input on theme changes
    window.addEventListener('theme-changed', () => {
        searchInput.focus();
    });

    // Rotating placeholders only if no value
    let currentPrompt = 0;
    const rotatePrompts = () => {
        if (!searchInput.value) {
            currentPrompt = (currentPrompt + 1) % prompts.length;
            searchInput.placeholder = prompts[currentPrompt];
        }
    };
    setInterval(rotatePrompts, 3000);

    // Show/hide enter hint based on input content
    function updateEnterHint() {
        if (searchInput.value.trim()) {
            enterHint.classList.add('visible');
        } else {
            enterHint.classList.remove('visible');
        }
    }

    // Initialize enter hint visibility
    updateEnterHint();

    // Listen for input changes
    searchInput.addEventListener('input', updateEnterHint);

    // Handle form submission
    function submitSearch() {
        if (searchInput.value.trim()) {  // Only submit if there's a value
            form.classList.add('submitting');
            form.submit();
        }
    }

    // Handle Enter key
    searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();  // Prevent default to avoid double submission
            submitSearch();
        }
    });

    // Handle button click
    const searchButton = document.querySelector('.search-btn');
    if (searchButton) {
        searchButton.addEventListener('click', (event) => {
            event.preventDefault();  // Prevent default button behavior
            submitSearch();
        });
    }

    // Handle form submit event
    form.addEventListener('submit', (event) => {
        if (!searchInput.value.trim()) {
            event.preventDefault();  // Prevent empty submissions
            return;
        }
        form.classList.add('submitting');
    });

    // Listen for caption-generated events from grid cells
    document.addEventListener('caption-generated', (event) => {
        if (searchInput && event.detail?.caption) {
            // Add visual feedback class
            searchInput.classList.add('caption-filled');
            searchInput.value = event.detail.caption;
            updateEnterHint();
            searchInput.focus();

            // Remove the visual feedback after a delay
            setTimeout(() => {
                searchInput.classList.remove('caption-filled');
            }, 1000);
        }
    });
"""


def search_input_form(
    initial_query: str = "",
    variant: str = "default",
    with_focus: bool = True,
    text_input_cls: str = "",
):
    return Form(
        text_input(
            placeholder="Looking for something specific?",
            left_section=icon("magnifying-glass"),
            right_section=Div(
                button("Search", size="xs", cls="search-btn"),
                button("Loading...", size="xs", cls="loading-btn"),
                cls="enter-hint",
            ),
            name="query",
            size="lg",
            id="search-input",
            content=initial_query,
            variant=variant,
            with_focus=with_focus,
            autocomplete="off",
            cls=text_input_cls,
        ),
        Style(SEARCH_STYLES),
        Script(SEARCH_SCRIPT.replace("${search_prompts}", str(SEARCH_PROMPTS))),
        style="pointer-events: auto;",
        method="GET",
        action="/search",
        cls="flex items-center w-full h-full px-sm sm:px-0",
    )


def homepage_search_box():
    """Search box component specifically styled for homepage."""
    return container(
        text(
            "We Make AI Work",
            size="3xl",
            cls="text-3xl sm:text-5xl md:text-6xl font-bold tracking-wide md:tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-high-contrast-text-slatetw to-solid-background-slatetw animate-fade-in",
        ),
        text(
            "Find relevant images through the power of advanced AI search",
            cls="text-sm sm:text-2xl font-semibold text-low-contrast-text md:tracking-wide",
        ),
        search_input_form(text_input_cls="ring-2 ring-high-contrast-text"),
        text(
            "Type to search or click any image to explore",
            cls="text-sm sm:text-base font-semibold text-low-contrast-text md:tracking-wide",
        ),
        size="md",
        style="pointer-events: none;",
        cls="gap-lg text-center transform translate-y-[21vh]",
    )


def toolbar_search_box(query: str = ""):
    """Search box component styled for the toolbar."""
    return search_input_form(
        initial_query=query,
        variant="unstyled",
        with_focus=False,
    )
