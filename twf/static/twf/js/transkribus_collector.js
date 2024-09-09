/**
 * This file contains the JavaScript code for the Transkribus Collector.
 * It is used to interact with the Transkribus API and to collect data from it.
 */


/**
 * This function is called when the user clicks the "Start Export" button.
 * @param project_id The ID of the project to export
 * @returns {Promise<void>} A promise that resolves when the export job is started
 */
async function start_export_job(project_id) {
    let button = $("#transkribusExport");
    let username = $("#transkribusUsername").val();
    let password = $("#transkribusPassword").val();

    button.prop("disabled", true);
    button.prop("value", "Requesting Export...");

    // The URL to the Django view that will handle the POST request
    let url = '/ajax/transkribus/export/request/';

    // Setup AJAX request
    await $.ajax({
        url: url,
        type: 'POST',
        data: {
            'project_id': project_id,
            'username': username,
            'password': password,
        },
        success: function(response) {
            // Handle success
            button.prop("value", "Export Requested");
            $("#transkribusExportStatus").prop("disabled", false);
            $("requestJobStatus").text("Whaaat");
        },
        error: function(xhr, errmsg, err) {
            // Handle error
            button.prop("value", "Error: " + xhr.responseJSON.message + " (Click to Retry)");
            button.prop("disabled", false);
        }
    });
}

/**
 * This function is called when the user clicks the "Check Export Status" button.
 * @param project_id The ID of the project to download
 * @returns {Promise<void>} A promise that resolves when the download is started
 */
async function check_export_status(project_id) {
    let button = $("#transkribusExportStatus");
    let resultBox = $("#jobStatus");
    let username = $("#transkribusUsername").val();
    let password = $("#transkribusPassword").val();

    button.prop("disabled", true);
    button.prop("value", "Checking Export Status...");
    resultBox.text("");

    // The URL to the Django view that will handle the POST request
    let url = '/ajax/transkribus/export/status/';

    // Setup AJAX request
    await $.ajax({
        url: url,
        type: 'POST',
        data: {
            'project_id': project_id,
            'username': username,
            'password': password,
        },
        success: function(response) {
            // Handle success
            let status = response.data.state;
            switch (status) {
                case "PENDING":
                    resultBox.text("Export is pending. Please wait.");
                    break;
                case "RUNNING":
                    resultBox.text("Export is running. " + response.data.description);
                    break;
                case "FAILED":
                    resultBox.text("Export failed. Please retry.");
                    break;
                case "FINISHED":
                    resultBox.text("Export finished. You can download the files now.");
                    if (response.data.result) {
                        $('#transkribusDownload').prop("disabled", false);
                    }
                    break;
                default:
                    resultBox.text("Export status unknown.");
            }
            console.log('Success:', response.data.state);
            button.prop("disabled", false);
            button.prop("value", "Check Status of Job");
        },
        error: function(xhr, errmsg, err) {
            // Handle error
            button.prop("disabled", false);
            button.prop("value",  "Error: " + xhr.responseJSON.message + " (Click to Retry)");
        }
    });
}

/**
 * This function is called when the user clicks the "Start Download" button.
 */
function updateProgress(downloadProgress, downloadProgressBar, startDownloadButton) {
    const evtSource = new EventSource('/ajax/transkribus/export/monitor/download/');
    evtSource.onmessage = function(event) {
        //console.log('Current progress:', event.data);
        let progress = parseInt(event.data); // Assuming progress data is a simple integer
        if (progress >= 100) {
            evtSource.close();  // Close the event source if the progress is 100
            console.log('Extraction completed');
        }
        downloadProgressBar.css('width', progress + '%').attr('aria-valuenow', progress).text(progress + '%');
    };
}
