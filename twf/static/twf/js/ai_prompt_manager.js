$(document).ready(function() {
    const saveButton = document.getElementById("savePrompt");
    const loadButton = document.getElementById("loadPrompt");
    const promptSelect = document.querySelector("select[name='saved_prompts']");
    const roleInput = document.querySelector("input[name='role_description']");
    const promptInput = document.querySelector("textarea[name='prompt']");

    $("#id_saved_prompts").select2({
        templateResult: formatDropdown,
        templateSelection: formatDropdown
    });
    updateDropdown(null);

    // Save Prompt
    saveButton.addEventListener("click", function() {

        const promptId = promptSelect.value;
        const role = roleInput.value;
        const promptText = promptInput.value;

        if (!promptText.trim()) {
            do_alert("Prompt text cannot be empty.", "warning");
            return;
        }
        if (!role.trim()) {
            do_alert("Prompt text cannot be empty.", "warning");
            return;
        }

        fetch("/ajax/save/prompt/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                prompt_id: promptId !== "--------" ? promptId : null,
                role: role,
                prompt: promptText
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                do_alert("Prompt saved successfully!", "success");
                // Update dropdown and select the new prompt
                updateDropdown(data.id);
            } else {
                do_alert("Error: " + data.error, "danger");
            }
        })
        .catch(error => do_alert("Error saving prompt.", "danger"));
    });

    // Function to update the dropdown
    function updateDropdown(selectedId) {
        fetch("/ajax/get/prompts/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.prompts) {
                $(promptSelect).empty();
                $(promptSelect).append(new Option("--------", "")); // Default option

                data.prompts.forEach(prompt => {
                    let truncatedPrompt = prompt.prompt.length > 50
                        ? prompt.prompt.substring(0, 50) + "…"
                        : prompt.prompt;

                    let $option = $(`<option></option>`)
                        .val(prompt.id)
                        .text(`${prompt.role} - ${truncatedPrompt}`)
                        .attr("data-role", prompt.role)
                        .attr("data-prompt", truncatedPrompt);
                    $(promptSelect).append($option);
                });

                // Reinitialize Select2
                $(promptSelect).select2({
                    templateResult: formatDropdown,
                    templateSelection: formatDropdown
                });

                // Select the newly saved prompt
                $(promptSelect).val(selectedId).trigger("change");
            }
        })
        .catch(error => do_alert("Error fetching prompts.", "danger"));
    }


    // Load Prompt
    loadButton.addEventListener("click", function() {
        console.log("Loading Prompt...");

        const promptId = promptSelect.value;
        if (!promptId || promptId === "--------") {
            do_alert("Please select a valid prompt.", "warning");
            return;
        }

        fetch("/ajax/load/prompt/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),  // CSRF protection
            },
            body: JSON.stringify({ prompt_id: promptId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.prompt) {
                roleInput.value = data.role;
                promptInput.value = data.prompt;
            } else {
                do_alert("Error loading prompt: " + data.error, "danger");
            }
        })
        .catch(error => do_alert("Error loading prompt." + error, "danger"));
    });

    // CSRF Token Helper Function
    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1] || "";
    }

    function do_alert(message, type="info") {
        const messagesContainer = document.querySelector(".messages");

        if (!messagesContainer) {
            console.warn("Messages container not found.");
            return;
        }

        // Bootstrap alert HTML
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type}`;
        alertDiv.role = "alert";
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close float-end" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        messagesContainer.appendChild(alertDiv);

        // Automatically remove the alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
    this.do_alert = do_alert;

    function formatDropdown(option) {
        if (!option.id) {
            return option.text;
        }

        let role = $(option.element).attr("data-role") || "Unknown Role";
        let promptText = $(option.element).attr("data-prompt") || "No prompt text available";

        return $(`<div><strong>${role}</strong><br><small>${promptText}</small></div>`);
    }
});
