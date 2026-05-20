
// 1. FLASHCARD ANSWER MODAL FUNCTIONALITY

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('answer-form');
    if (!form) return; 

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




// 2. DECK SEARCH & TAG FILTER FUNCTIONALITY AND TAG COLORS

document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('deckSearch');
    
    // Function to generate a consistent color based on the tag name 
    function applyDynamicTagColors() {
        const badges = document.querySelectorAll('.tag-badge');
        badges.forEach(function(badge) {
            const text = badge.textContent.trim().toLowerCase();
            if (!text) return;

            // Generate a simple hash value from the text 
            let hash = 0;
            for (let i = 0; i < text.length; i++) {
                hash = text.charCodeAt(i) + ((hash << 5) - hash);
            }

            // Convert hash to a readable color 
            const hue = Math.abs(hash) % 360;
            const saturation = 70; 
            const lightness = 85;  
            const textColor = lightness > 60 ? '#111111' : '#ffffff';

            // Apply directly to the element's style property
            badge.style.backgroundColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
            badge.style.color = textColor;
            badge.style.border = 'none';
        });
    }

    
    applyDynamicTagColors();

   
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


    const urlParams = new URLSearchParams(window.location.search);
    const filterParam = urlParams.get('filterTag');
    if (filterParam && searchInput) {
        searchInput.value = filterParam;
        filterDecks(filterParam);
    }

    // If searchInput doesn't exist, we are inside a deck page
    if (!searchInput) {
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('search-tag')) {
                e.preventDefault();
                e.stopPropagation();
                
                const clickedTag = e.target.getAttribute('data-tag') || e.target.textContent.toLowerCase().trim();
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

            const clickedTag = e.target.getAttribute('data-tag') || e.target.textContent.toLowerCase().trim();
            
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