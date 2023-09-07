// JavaScript for sliding down collapsible dropdowns
document.addEventListener("DOMContentLoaded", function() {
    const toggleButtons = document.querySelectorAll(".toggle-dropdown");
    const dropdownContents = document.querySelectorAll(".dropdown-content");
    
    toggleButtons.forEach((button, index) => {
        button.addEventListener("click", function() {
            const dropdownContent = dropdownContents[index];
            
            // Close all dropdowns except the one that was clicked
            dropdownContents.forEach((content, i) => {
                if (i !== index) {
                    content.style.maxHeight = null;
                }
            });

            if (dropdownContent.style.maxHeight) {
                dropdownContent.style.maxHeight = null;
            } else {
                dropdownContent.style.maxHeight = dropdownContent.scrollHeight + "px";
            }
        });
    });
});

