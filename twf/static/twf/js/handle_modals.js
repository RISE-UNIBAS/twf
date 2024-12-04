$(document).ready(function () {
  const normalModal = new bootstrap.Modal($('#confirmModal')[0]);
  const normalConfirmButton = $('#confirmActionButton');

  let taskFunction = null; // Function to execute on confirmation

  $('.show-confirm-modal').on('click', function (event) {
    event.preventDefault(); // Prevent default button behavior

    // Set modal message dynamically
    const message = $(this).data('message') || 'Are you sure you want to proceed?';
    $('#confirmModal .modal-body').text(message);

    // Prepare the action based on button's data attributes
    const button = $(this);
    const startUrl = button.data('start-url');
    const progressUrlBase = button.data('progress-url-base');
    const progressBarId = button.data('progress-bar-id');
    const logTextareaId = button.data('log-textarea-id');

    // Serialize form data
    const form = button.closest('form');
    const formData = form.serialize(); // Collect all form fields

    // Define the task function
    taskFunction = () => {
      if (startUrl) {
        startTask(
          startUrl,
          progressUrlBase,
          progressBarId,
          logTextareaId,
          formData // Include serialized form data
        );
      }
    };

    // Show the modal
    normalModal.show();
  });

  // Execute the task when Confirm is clicked
  normalConfirmButton.on('click', function () {
    if (taskFunction) {
      taskFunction(); // Execute the task function
    }
    normalModal.hide();
  });
});
