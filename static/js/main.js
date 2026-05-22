
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
// Drag and Drop for Deck Import
const dropZone = document.getElementById("drop-zone");
if (dropZone) {
const fileInput = document.getElementById("deck_file");
const fileName = document.getElementById("file-name");
fileInput.addEventListener("change", function () {
    fileName.textContent =
        this.files[0]?.name || "No file chosen";
});
dropZone.addEventListener("dragover", function (e) {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});
dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("drag-over");
});
dropZone.addEventListener("drop", function (e) {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".json")) {
        fileInput.files = e.dataTransfer.files;
        fileName.textContent = file.name;
    } else {
        fileName.textContent =
            "Please upload a JSON file.";
    }
});

}

document.addEventListener('DOMContentLoaded', () => {
    
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');

    if (toggleSwitch) {
        // We removed the setup logic here, because the inline HTML scripts handled it!
        
        // Listen for when the user clicks the switch
        toggleSwitch.addEventListener('change', function(e) {
            if (e.target.checked) {
                // Switch flipped ON -> Turn on Dark Mode and save to memory
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                // Switch flipped OFF -> Turn on Light Mode and save to memory
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }
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

             
            let hash = 0;
            for (let i = 0; i < text.length; i++) {
                hash = text.charCodeAt(i) + ((hash << 5) - hash);
            }

             
            const hue = Math.abs(hash) % 360;
            const saturation = 70; 
            const lightness = 85;  
            const textColor = lightness > 60 ? '#111111' : '#ffffff';

            
            badge.style.backgroundColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
            badge.style.color = textColor;
            badge.style.border = 'none';
        });
    }

    // Run the coloring logic immediately so it applies to ALL pages
    applyDynamicTagColors();

    // If there's no search bar on this page (like index.html), stop here
    if (!searchInput) return;

    
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

   
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        filterDecks(searchTerm);
    });

    
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
