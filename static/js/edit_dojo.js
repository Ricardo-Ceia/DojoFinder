$(document).ready(function() {
    // Fix the selector - it should be '.btn-primary' for class selection
    $('.btn-primary').on('click', function(e) {
        e.preventDefault(); // Prevent default form submission

        // Get all form data including schedules
        let formData = new FormData($('form')[0]);
        
        $.ajax({
            url: `/edit_dojo/${dojoId}`, // Make sure dojoId is defined
            type: 'POST',
            data: formData,
            processData: false,  // Don't process the data
            contentType: false,  // Don't set content type
            success: function(response) {
                console.log('Success:', response);
                // Redirect or show success message
                window.location.href = '/manage_dojos';
            },
            error: function(error) {
                console.log('Error:', error);
                // Show error message to user
            }
        });
    });
});