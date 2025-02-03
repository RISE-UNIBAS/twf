$(document).ready(function () {
  // Initialize both modals
  const normalModal = new bootstrap.Modal($('#confirmModal')[0]);
  const dangerModal = new bootstrap.Modal($('#confirmDangerModal')[0]);

  // Single event listener for both types of modals
  $('.show-confirm-modal, .show-danger-modal').on('click', function (event) {
    event.preventDefault(); // Prevent default button behavior

    // Identify which modal to show
    const isDanger = $(this).hasClass('show-danger-modal');
    const modal = isDanger ? dangerModal : normalModal;
    const modalBody = isDanger ? '#confirmDangerModal .modal-body' : '#confirmModal .modal-body';
    const confirmButton = isDanger ? $('#confirmDangerActionButton') : $('#confirmActionButton');

    // Set modal message dynamically
    const message = $(this).data('message') || 'Are you sure you want to proceed?';
    $(modalBody).html(message);

    // Prepare the action based on button's data attributes
    const button = $(this);
    let taskFunction = null;
    const redirectUrl = button.data('redirect-url');
    const startTaskUrl = button.data('start-url');

    // Automatically find the closest form
    const form = button.closest("form");
    if (form.length > 0) {
      taskFunction = () => form.submit(); // Submit the correct form
    }
    if (redirectUrl) {
      taskFunction = () => (window.location.href = redirectUrl); // Redirect to the specified URL
    }
    if (startTaskUrl) {
      const progressUrlBase = button.data('progress-url-base');
      const progressBarId = button.data('progress-bar-id');
      const logTextareaId = button.data('log-textarea-id');

      // Extract form data and pass it to startTask
      let formData = {};
      if (form.length > 0) {
        const formEntries = new FormData(form[0]).entries();
        formData = Object.fromEntries(formEntries);
      }

      taskFunction = () => {
        console.log("Starting Celery task at:", startTaskUrl, "with data:", formData);
        startTask(startTaskUrl, progressUrlBase, progressBarId, logTextareaId, formData);
      };
    }

    // Attach task function to confirm button
    confirmButton.off('click').on('click', function () {
      if (taskFunction) {
        taskFunction(); // Execute the task function (submit or redirect)
      }
      modal.hide();
    });

    // Show the appropriate modal
    modal.show();
  });
});
