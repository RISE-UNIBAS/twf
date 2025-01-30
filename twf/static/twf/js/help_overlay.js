document.addEventListener("DOMContentLoaded", function () {
    const helpButton = document.getElementById("helpButton");
    const helpOverlay = document.getElementById("helpOverlay");
    const closeHelp = document.querySelector(".close-help");
    const helpText = document.getElementById("helpText");

    // Function to get page-specific help content
    function loadHelpContent() {
        let pageName = document.body.dataset.page; // Get the view name from <body>

        if (!pageName) {
            helpText.innerHTML = "<p>No help content available for this page.</p>";
            return;
        }

        if (pageName.startsWith("twf:")) {
            pageName = pageName.replace("twf:", "");
        }

        const helpUrl = `/help/${pageName}/`; // URL to fetch help content

        fetch(helpUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Help content not found");
                }
                return response.text();
            })
            .then(html => {
                helpText.innerHTML = html; // Insert the fetched HTML into the help overlay
            })
            .catch(error => {
                helpText.innerHTML = "<p>Help content could not be loaded.</p>";
                console.error("Error loading help:", error);
            });
    }

    // Show overlay
    helpButton.addEventListener("click", function () {
        loadHelpContent();
        helpOverlay.classList.add("show");
    });

    // Hide overlay
    closeHelp.addEventListener("click", function () {
        helpOverlay.classList.remove("show");
    });

    // Close overlay when clicking outside
    document.addEventListener("click", function (event) {
        if (!helpOverlay.contains(event.target) && !helpButton.contains(event.target)) {
            helpOverlay.classList.remove("show");
        }
    });
});
