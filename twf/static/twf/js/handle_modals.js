$(document).ready(function () {
  // Initialize modals
  const normalModal = new bootstrap.Modal($('#confirmModal')[0]);
  const dangerModal = new bootstrap.Modal($('#confirmDangerModal')[0]);

  const normalConfirmButton = $('#confirmActionButton');
  const dangerConfirmButton = $('#confirmDangerActionButton');

  let formElement = null;
  let selectedButton = null;

  // Attach click event to buttons
  $('.show-confirm-modal, .show-confirm-danger-modal').on('click', function (event) {
    event.preventDefault(); // Prevent default form submission

    // Store the form and button elements
    formElement = $(this).closest('form');
    selectedButton = $(this);

    // Set modal message dynamically
    const message = selectedButton.data('message');
    if ($(this).hasClass('show-confirm-danger-modal')) {
      $('#confirmDangerModal .modal-body').text(message);
      dangerModal.show();
    } else {
      $('#confirmModal .modal-body').text(message);
      normalModal.show();
    }
  });

  // Confirm actions for normal modal
  normalConfirmButton.on('click', function () {
    if (formElement && selectedButton) {
      // Trigger form submission with the selected button
      $('<input>')
        .attr({
          type: 'hidden',
          name: selectedButton.attr('name'),
          value: selectedButton.val(),
        })
        .appendTo(formElement);

      formElement.submit();
    }
    normalModal.hide();
  });

  // Confirm actions for danger modal
  dangerConfirmButton.on('click', function () {
    if (formElement && selectedButton) {
      // Trigger form submission with the selected button
      $('<input>')
        .attr({
          type: 'hidden',
          name: selectedButton.attr('name'),
          value: selectedButton.val(),
        })
        .appendTo(formElement);

      formElement.submit();
    }
    dangerModal.hide();
  });
});
