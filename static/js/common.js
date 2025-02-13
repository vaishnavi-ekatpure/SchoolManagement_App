$(document).ready(function() {
    $('.select2').select2({
      minimumResultsForSearch: -1
    });

    $(document).on('click', '.confirm-delete', function (e) {
      e.preventDefault(); 
      var deleteUrl = $(this).data('href'); 
      $('#confirmDeleteBtn').attr('href', deleteUrl); 
      $('#deleteConfirmationModal').modal('show');
    });
  
});