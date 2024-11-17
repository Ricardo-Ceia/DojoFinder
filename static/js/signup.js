$(document).ready(function() {
    $('.signup-form').on('submit', function(e) {
        e.preventDefault(); 
        $.ajax({
            url: '/signup_form',
            method: 'POST',
            data: $(this).serialize(),
            success:function(response){
                window.location.href = response['redirect'];
            },
            error: function(error) {
                if (error.status === 404 || error.status === 400 || error.status === 500) {
                    const responseJson = JSON.parse(error.responseText);
                    $('.error-container').html(`<p>${responseJson['error']}</p>`);

                    // Call hideError after 3 seconds
                    setTimeout(hideError, 3000);
                }
            }
        });
    });

    function hideError() {
        $('.error-container').fadeOut('slow', function() {
            $(this).empty().show(); // Optional: empty the container and make it visible again for future errors
        });
    }
});
