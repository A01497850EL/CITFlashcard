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