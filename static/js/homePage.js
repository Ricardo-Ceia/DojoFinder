$(document).ready(function() {
    function showError(message) {
        $('#error-message').text(message);
        $('#error-container').show();
    }
    
    function hideError() {
        $('#error-container').hide();
    }

    // Add Dojo button handler
    $('.add-dojo-button').on('click', function(e) {
        e.preventDefault(); // Prevent default button behavior
        $.ajax({
            url: '/premium_dojo_form',
            success: function(data) {
                $('body').append(data);
                $('#formOverlay').css('display', 'flex');
            },
            error: function() {
                console.error('Failed to load add_dojo_form.html');
            }
        }); 
    });

    // Search form handler
    $('#search-form').on('submit', function(e) {
        e.preventDefault(); // Prevent form submission

        const city = $('input[name="location"]').val().trim();

        // Validation
        if (!city) {
            showError('Please enter a city name');
            return;
        }

        if (!/^[a-zA-Z\s-]+$/.test(city)) {
            showError('Please enter a valid city name');
            return;
        }

        if (city.length < 2 || city.length > 50) {
            showError('City name must be between 2 and 50 characters');
            return;
        }

        hideError();

        // Show loading state
        $('#response').html('<div class="loading">Searching dojos...</div>');

        // Make AJAX request
        $.ajax({
            url: '/get_dojos',
            method: 'POST',
            data: { location: city },
            success: function(response) {
                // Log the response to see its content
                console.log('AJAX Response:', response);
                
                // Update the #response div with the results
                $('#response').html(response);
    
                // Scroll to the #response div with smooth scroll
                $('html, body').animate({
                    scrollTop: $('#response').offset().top
                }, 1000); // Scroll takes 1000ms (1 second)
            },
            error: function(xhr, status, error) {
                // Log detailed error information
                console.log("Error details:", {
                    response: xhr.responseText,
                    status: status,
                    error: error
                });
                $('#response').html('<p>Error fetching dojo data. Please try again later.</p>');
            }
        });
    });

    // Clear error on input
    $('input[name="location"]').on('input', function() {
        hideError();
    });
});