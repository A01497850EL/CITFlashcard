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

document.addEventListener('DOMContentLoaded', () => {

    
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');

    // checks to see if the toggle switch actually exists on the page
    if (toggleSwitch) {

        // Check to see if they were already in Dark Mode
        const currentTheme = localStorage.getItem('theme');

        if (currentTheme) {
            document.documentElement.setAttribute('data-theme', currentTheme);
            // If they chose dark mode, flip the switch to on
            if (currentTheme === 'dark') {
                toggleSwitch.checked = true;
            }
        }

        // If user the user toggles the switch
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
