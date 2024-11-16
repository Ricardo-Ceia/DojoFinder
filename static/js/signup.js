$(document).ready(function() {
    $('.signup-form').on('submit', function(e) {
        e.preventDefault(); 
        $.ajax({
            url: '/signup_form',
            method: 'POST',
            data: $(this).serialize(),
            error: function(error) {
                if (error.status === 404 || error.status === 400 || error.status === 500) {
                    const responseJson = JSON.parse(error.responseText);
                    $('.error-container').html(`<p>${responseJson['error']}</p>`);
                }
            }
        });
    });
});
