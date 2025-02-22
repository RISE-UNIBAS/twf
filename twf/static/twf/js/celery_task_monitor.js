(function() {
    let lastMessage = "";

    /**
     * Starts a task by sending an AJAX request to the provided URL
     * and begins monitoring its progress.
     *
     * @param {string} startUrl - The URL to start the task.
     * @param {string} progressUrlBase - The base URL to poll the task progress, appended with task ID.
     * @param {string} progressBarId - The ID of the progress bar to update.
     * @param {string} logTextareaId - The ID of the textarea to display logs.
     * @param {object} data - Additional data to send with the start request.
     */
    function startTask(startUrl, progressUrlBase, progressBarId, logTextareaId, data) {
        const queryString = new URLSearchParams(data).toString();
        lastMessage = "";

        // Clear the log before starting
        $(logTextareaId).text('');

        // Reset the progress bar
        const progressBar = $(progressBarId);
        progressBar.css('width', '0%');
        progressBar.removeClass('bg-success bg-danger'); // Remove any existing colors
        progressBar.addClass('bg-dark');

        console.log('Task URL:', startUrl);
        console.log('Task Data:', data);

        // Send AJAX request to start the task
        $.ajax({
            url: startUrl,
            method: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function(data) {
                let taskId = data.task_id;
                pollTaskProgress(taskId, progressUrlBase, progressBarId, logTextareaId);
            },
            error: function(error) {
                console.error("Error starting task:", error.responseText);
                $(logTextareaId).append('Error starting task.\n');
            }
        });
    }

    /**
     * Polls the task progress and updates the progress bar and logs.
     *
     * @param {string} taskId - The ID of the task to monitor.
     * @param {string} progressUrlBase - The base URL to fetch task progress, appended with task ID.
     * @param {string} progressBarId - The ID of the progress bar to update.
     * @param {string} logTextareaId - The ID of the textarea to display logs.
     */
    function pollTaskProgress(taskId, progressUrlBase, progressBarId, logTextareaId) {
        let url = progressUrlBase + taskId + '/';

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const progressBar = $(progressBarId);
                const status = data.status.toUpperCase();

                if (status === 'PENDING' || status === 'STARTED') {
                    progressBar.css('width', '100%');
                    progressBar.addClass('bg-dark progress-bar-striped progress-bar-animated');

                    setTimeout(function() {
                        pollTaskProgress(taskId, progressUrlBase, progressBarId, logTextareaId);
                    }, 800);
                }
                else if (status === 'PROGRESS') {
                    let progress = (data.current / data.total) * 100;
                    if (isNaN(progress)) {
                        progress = 0;
                    }
                    progressBar.css('width', progress + '%');
                    progressBar.removeClass('progress-bar-striped progress-bar-animated');
                    progressBar.text(progress.toFixed(2) + '%');

                    if (data.text) {
                        const logTextarea = $(logTextareaId);
                        let currentLog = logTextarea.val().trim();
                        console.log('New log:', data.text);
                        console.log('Last message:', lastMessage);
                        if (data.text === lastMessage) {
                            // If it's the same message, just append a dot
                            logTextarea.val(currentLog + ".");
                        } else {
                            // New message, add it as a new line
                            logTextarea.val(currentLog + "\n" + data.text);
                            lastMessage = data.text; // Update last message
                        }
                        scrollToBottom(logTextareaId);
                    }

                    setTimeout(function() {
                        pollTaskProgress(taskId, progressUrlBase, progressBarId, logTextareaId);
                    }, 800);
                } else if (status === 'SUCCESS') {
                    progressBar.css('width', '100%');
                    progressBar.removeClass('bg-dark'); // Remove the dark color
                    progressBar.addClass('bg-success'); // Change the progress bar color to red
                    progressBar.text('Completed');
                    $(logTextareaId).append('Task completed\n');

                    if (data.result.download_url) {
                        $(logTextareaId).append("Click here to download: " + data.result.download_url + "\n");

                        // Automatically trigger file download
                        const downloadLink = document.createElement("a");
                        downloadLink.href = data.result.download_url;
                        downloadLink.download = "exported_documents.zip"; // Default name
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                    }

                    scrollToBottom(logTextareaId);
                } else if (status === 'FAILURE') {
                    progressBar.css('width', '100%');
                    progressBar.removeClass('bg-dark'); // Remove the dark color
                    progressBar.addClass('bg-danger'); // Change the progress bar color to red
                    progressBar.text('Failed');
                    $(logTextareaId).append('Error: ' + data.error + '\n');
                    scrollToBottom(logTextareaId);
                }
            })
            .catch(error => {
                console.error('Error polling task progress:', error);
                $(logTextareaId).append('Error polling task progress.\n');
            });
    }

    /**
     * Scrolls to the bottom of a textarea.
     *
     * @param {string} textareaId - The ID of the textarea to scroll.
     */
    function scrollToBottom(textareaId) {
        const textarea = $(textareaId);
        textarea.scrollTop(textarea[0].scrollHeight);
    }

    // Expose the startTask function to be used globally
    window.startTask = startTask;
})();
