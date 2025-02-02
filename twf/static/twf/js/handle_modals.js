$(document).ready(function () {
  const normalModal = new bootstrap.Modal($('#confirmModal')[0]);

  const dangerModal = new bootstrap.Modal($('#confirmDangerModal')[0]);

  const normalConfirmButton = $('#confirmActionButton');
  const dangerConfirmButton = $('#confirmDangerActionButton');

  let taskFunction = null; // Function to execute on confirmation
  let redirectUrl = null; // URL to redirect after confirmation
  let startTaskUrl = null; // URL to start a task

  $('.show-confirm-modal').on('click', function (event) {
    event.preventDefault(); // Prevent default button behavior

    // Set modal message dynamically
    const message = $(this).data('message') || 'Are you sure you want to proceed?';
    $('#confirmModal .modal-body').html(message);

    // Prepare the action based on button's data attributes
    const button = $(this);
    redirectUrl = button.data('redirect-url'); // Get redirect URL
    startTaskUrl = button.data('start-url'); // Get start task URL

    // If a form exists, prepare to handle it
    const form = button.closest("form"); // Automatically find the closest form
    if (form) {
      taskFunction = () => {
        form.submit(); // Submit the correct form
      };
    }
    if (redirectUrl) {
      // If no form is specified but a redirect URL is present
      taskFunction = () => {
        window.location.href = redirectUrl; // Redirect to the specified URL
      };
    }
    if (startTaskUrl) {
      const progressUrlBase = button.data('progress-url-base');
      const progressBarId = button.data('progress-bar-id');
      const logTextareaId = button.data('log-textarea-id');

      taskFunction = () => {
        // Call the function to start the task
        startTask(startTaskUrl, progressUrlBase, progressBarId, logTextareaId, {});
      };
    }

    // Show the modal
    normalModal.show();
  });

  $('.show-danger-modal').on('click', function (event) {
    event.preventDefault(); // Prevent default button behavior

    // Set modal message dynamically
    const message = $(this).data('message') || 'Are you sure you want to proceed?';
    $('#confirmDangerModal .modal-body').html(message);

    // Prepare the action based on button's data attributes
    const button = $(this);
    redirectUrl = button.data('redirect-url'); // Get redirect URL
    startTaskUrl = button.data('start-url'); // Get start task URL

    // If a form exists, prepare to handle it
    const form = button.closest("form"); // Automatically find the closest form
    if (form) {
      taskFunction = () => {
        form.submit(); // Submit the correct form
      };
    }
    if (redirectUrl) {
      // If no form is specified but a redirect URL is present
      taskFunction = () => {
        window.location.href = redirectUrl; // Redirect to the specified URL
      };
    }
    if(startTaskUrl) {
      const progressUrlBase = button.data('progress-url-base');
      const progressBarId = button.data('progress-bar-id');
      const logTextareaId = button.data('log-textarea-id');

      taskFunction = () => {
        // Call the function to start the task
        startTask(startTaskUrl, progressUrlBase, progressBarId, logTextareaId, {});
      };
    }

    // Show the modal
    dangerModal.show();

  });

  // Execute the task when Confirm is clicked
  normalConfirmButton.on('click', function () {
    if (taskFunction) {
      taskFunction(); // Execute the task function (submit or redirect)
    }
    normalModal.hide();
  });

  dangerConfirmButton.on('click', function () {
      if (taskFunction) {
      taskFunction(); // Execute the task function (submit or redirect)
      }
      dangerModal.hide();
  });

});
