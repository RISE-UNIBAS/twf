(function() {
    let lastMessage = "";
    const startButtonId = "#button-id-startbatch";
    const cancelButtonId = "#button-id-cancelbatch";

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
        
        // Remove any existing task detail buttons
        $('[id^="task-details-btn-"]').remove();

        // Reset the progress bar
        const progressBar = $(progressBarId);
        progressBar.css('width', '0%');
        progressBar.text('Running...');
        progressBar.removeClass('bg-success bg-danger'); // Remove any existing colors
        progressBar.addClass('bg-dark'); // Add a dark color

        // Send AJAX request to start the task
        $.ajax({
            url: startUrl,
            method: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function(data) {
                let taskId = data.task_id;

                 $(cancelButtonId).prop("disabled", false);
                 $(startButtonId).prop("disabled", true);
                 $(cancelButtonId).data("task-id", taskId); // Store the task ID for canceling

                pollTaskProgress(taskId, progressUrlBase, progressBarId, logTextareaId);
            },
            error: function(error) {
                $(logTextareaId).append('Error starting task.\n');
                $(logTextareaId).append(error.responseText + '\n');
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

                    // If we have full text available, use it (complete log)
                    if (data.full_text) {
                        console.log("Full text available:", data.full_text.length, "chars");
                        const logTextarea = $(logTextareaId);
                        logTextarea.val(data.full_text);
                        
                        // If we have a database task ID, add/update the task link button
                        if (data.db_task_id) {
                            console.log("Found DB task ID:", data.db_task_id);
                            const taskUrl = '/project/task/' + data.db_task_id + '/view/';
                            const detailsButtonId = 'task-details-btn-' + taskId;
                            
                            if (!$('#' + detailsButtonId).length) {
                                const detailsButton = $('<a>', {
                                    id: detailsButtonId,
                                    text: 'View Task Progress',
                                    href: taskUrl,
                                    target: '_blank',
                                    class: 'btn btn-sm btn-secondary ml-2 mt-2'
                                });
                                $(logTextareaId).after(detailsButton);
                            }
                        }
                        
                        scrollToBottom(logTextareaId);
                    } 
                    // Fallback to old behavior if full_text is not available
                    else if (data.text) {
                        console.log("Only partial text available");
                        const logTextarea = $(logTextareaId);
                        let currentLog = logTextarea.val().trim();

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
                    progressBar.removeClass("progress-bar-animated")
                    progressBar.addClass('bg-success'); // Change the progress bar color to green
                    progressBar.text('Completed');
                    $(logTextareaId).append('Task completed\n');
                    
                    // Add a link to the task details page - just show the URL in the textarea
                    const taskUrl = data.db_task_id ? 
                        '/project/task/' + data.db_task_id + '/view/' : 
                        '/project/task_monitor/'; // Fallback to task monitor if no DB ID
                    
                    $(logTextareaId).append('View complete task log at: ' + taskUrl + '\n');
                    
                    // Create a button below the textarea that links to the task details
                    const detailsButtonId = 'task-details-btn-' + taskId;
                    if (!$('#' + detailsButtonId).length) {
                        const detailsButton = $('<a>', {
                            id: detailsButtonId,
                            text: 'View Complete Task Log',
                            href: taskUrl,
                            target: '_blank',
                            class: 'btn btn-sm btn-info ml-2 mt-2'
                        });
                        $(logTextareaId).after(detailsButton);
                    }

                    $(cancelButtonId).prop("disabled", true);
                    $(startButtonId).prop("disabled", false);

                    if (data.result) {
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
                        if (data.result.ai_result) {
                            format_ai_result(data.result.ai_result);
                        }
                    }

                    scrollToBottom(logTextareaId);
                } else if (status === 'FAILURE') {
                    progressBar.css('width', '100%');
                    progressBar.removeClass('bg-dark'); // Remove the dark color
                    progressBar.addClass('bg-danger'); // Change the progress bar color to red
                    progressBar.text('Failed');
                    $(logTextareaId).append('Error: ' + data.error + '\n');
                    
                    // Add a link to the task details page - just show the URL in the textarea
                    const taskUrl = data.db_task_id ? 
                        '/project/task/' + data.db_task_id + '/view/' : 
                        '/project/task_monitor/'; // Fallback to task monitor if no DB ID
                    
                    $(logTextareaId).append('View complete task log at: ' + taskUrl + '\n');
                    
                    // Create a button below the textarea that links to the task details
                    const detailsButtonId = 'task-details-btn-' + taskId;
                    if (!$('#' + detailsButtonId).length) {
                        const detailsButton = $('<a>', {
                            id: detailsButtonId,
                            text: 'View Complete Task Log',
                            href: taskUrl,
                            target: '_blank',
                            class: 'btn btn-sm btn-danger ml-2 mt-2'
                        });
                        $(logTextareaId).after(detailsButton);
                    }
                    scrollToBottom(logTextareaId);
                }
            })
            .catch(error => {
                console.error('Error polling task progress:', error);
                $(logTextareaId).append('Error polling task progress.\n');
            });
    }

    function cancelTask(cancelUrlBase) {
        const cancelButton = $(cancelButtonId);
        const taskId = cancelButton.data("task-id");

        if (!taskId) {
            console.error("No task ID found for cancellation.");
            return;
        }

        // Show the confirmation modal (assuming you have a Bootstrap modal)
        if (!confirm("Are you sure you want to cancel the task?")) {
            return; // Exit if the user cancels
        }

        // Send request to cancel the task
        $.ajax({
            url: '/celery/cancel/' + taskId + '/',
            method: 'POST',
            success: function(response) {
                console.log("Task canceled successfully:", response);

                // Disable the cancel button and re-enable the run button
                cancelButton.prop("disabled", true);
                $(runButtonId).prop("disabled", false);
                do_alert("Task canceled successfully!", "success");
            },
            error: function(error) {
                console.error("Error canceling task:", error.responseText);
                do_alert("Error canceling task.", "danger");
            }
        });
    }

    // Expose the cancel function globally
    window.cancelTask = cancelTask;

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
