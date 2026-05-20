// ==========================================
// 1. FLASHCARD ANSWER MODAL FUNCTIONALITY
// ==========================================
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('answer-form');
    if (!form) return; // Safely exits ONLY this block if not on the study page

    const inputSection = document.getElementById('input-section');
    const feedbackArea = document.getElementById('feedback-area');
    const correctMsg = document.getElementById('correct-msg');
    const wrongMsg = document.getElementById('wrong-msg');
    const overrideField = document.getElementById('override-field');
    const userAnswerInput = document.getElementById('user-answer');

    const actualAnswer = form.getAttribute('data-answer').trim().toLowerCase();

    form.onsubmit = function(e) {
        if (overrideField.value === "true" || !feedbackArea.classList.contains('hidden')) {
            return true;
        }

        e.preventDefault();
        const val = userAnswerInput.value.trim().toLowerCase();

        inputSection.classList.add('hidden');
        feedbackArea.classList.remove('hidden');

        if (val === actualAnswer) {
            correctMsg.classList.remove('hidden');
            document.getElementById('override-btn').classList.add('hidden');
        } else {
            document.getElementById('your-answer-display').innerHTML = "<strong>Your Answer:</strong> " + userAnswerInput.value;
            wrongMsg.classList.remove('hidden');
        }
    };

    document.getElementById('override-btn').onclick = function() {
        overrideField.value = "true";
        form.submit();
    };
});


// ==========================================
// 2. DECK SEARCH & TAG FILTER FUNCTIONALITY
// ==========================================
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('deckSearch');
    
    // Core filtering logic helper
    function filterDecks(searchTerm) {
        const deckContainers = document.querySelectorAll('.decks-grid > .flashy-relative-container');

        deckContainers.forEach(function(container) {
            const deckItem = container.querySelector('.deck-item');
            if (!deckItem) return;

            const name = deckItem.querySelector('.deck-item-head')?.textContent.toLowerCase() || '';
            const description = deckItem.querySelector('.deck-item-sub')?.textContent.toLowerCase() || '';
            
            const tags = Array.from(deckItem.querySelectorAll('.tag-badge'))
                .map(tag => tag.textContent.toLowerCase())
                .join(' ');

            if (name.includes(searchTerm) || description.includes(searchTerm) || tags.includes(searchTerm)) {
                container.style.display = '';
            } else {
                container.style.display = 'none';
            }
        });
    }

    // Check if we just redirected here via a tag click from an individual deck page
    const urlParams = new URLSearchParams(window.location.search);
    const filterParam = urlParams.get('filterTag');
    if (filterParam && searchInput) {
        searchInput.value = filterParam;
        filterDecks(filterParam);
    }

    // Exit early if the search input doesn't exist on this page
    if (!searchInput) {
        // If we are on an individual deck page, redirect clicks to the main view with a query string
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('search-tag')) {
                const clickedTag = e.target.getAttribute('data-tag');
                window.location.href = "/decks?filterTag=" + encodeURIComponent(clickedTag);
            }
        });
        return;
    }

    // 1. Listen for typing in the search bar
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        filterDecks(searchTerm);
    });

    // 2. Listen for clicks on the tag badges (Main Grid View)
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('search-tag')) {
            e.preventDefault();
            e.stopPropagation();

            const clickedTag = e.target.getAttribute('data-tag');
            
            // Toggle behavior: if already searching this tag, clear it. Otherwise, search it.
            if (searchInput.value.toLowerCase().trim() === clickedTag) {
                searchInput.value = '';
                filterDecks('');
            } else {
                searchInput.value = clickedTag;
                filterDecks(clickedTag);
            }
        }
    });
});