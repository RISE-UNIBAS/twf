(function() {
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
                console.log('Task Progress Data:', data); // Debug the full response
                const progressBar = $(progressBarId);
                const status = data.status.toUpperCase();

                if (status === 'PROGRESS' || status === 'PENDING') {
                    let progress = (data.current / data.total) * 100;
                    progressBar.css('width', progress + '%');
                    progressBar.text(progress.toFixed(2) + '%');
                    $(logTextareaId).append(data.text + '\n');
                    scrollToBottom(logTextareaId);

                    setTimeout(function() {
                        pollTaskProgress(taskId, progressUrlBase, progressBarId, logTextareaId);
                    }, 800); // Adjust the polling interval if needed
                } else if (status === 'SUCCESS') {
                    progressBar.css('width', '100%');
                    progressBar.removeClass('bg-dark'); // Remove the dark color
                    progressBar.addClass('bg-success'); // Change the progress bar color to red
                    progressBar.text('Completed');
                    $(logTextareaId).append('Task completed\n' + data.result.text + '\n');
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
