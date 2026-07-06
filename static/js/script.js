/* SmartPatent - Premium Client Scripting */

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    
    // Auto-intercept main generation submissions to render smooth loading screens
    if (form && form.action.includes("/generate_draft")) {
        form.addEventListener("submit", () => {
            let overlay = document.querySelector(".loading-overlay");
            if (!overlay) {
                overlay = document.createElement("div");
                overlay.className = "loading-overlay";
                overlay.innerHTML = `
                    <div class="spinner"></div>
                    <div class="loading-text">Analyzing invention details, querying global databases, and generating your patent draft...</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill"></div>
                    </div>
                `;
                document.body.appendChild(overlay);
            }
            overlay.style.display = "flex";
        });
    }
});
