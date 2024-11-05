$(document).ready(function() {
    //doc is ready

    function showError(message) {
        console.error('Error:', message);
        $('#error-message').text(message);
        $('#error-container').fadeIn(300);
    }
    
    function hideError() {
        $('#error-container').fadeOut(300);
    }

    $('.add-dojo-button').on('click',function(e) {
$.ajax({
    url: '/premium_dojo_form',
    success: function(data) {
        $('body').append(data);
        // Show the form immediately after it's appended
        $('#formOverlay').css('display', 'flex');
    },
    error: function() {
        console.error('Failed to load add_dojo_form.html');
    }
}); 
});

// Trigger the animation for the h1 on page load
$('.hero-content h1').css('opacity', 1).addClass('fadeInUp');

$('#search-form').on('submit', function(e) {
    e.preventDefault(); // Prevent the form from reloading the page

    const city = $('input[name="location"]').val().trim(); // Get the city value

    if(!city){
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

    // Make AJAX request to the backend
    $.ajax({
        url: '/get_dojos',
        method: 'POST',
        data: { location: city },
        success: function(response) {
            // Update the #response div with the results
            $('#response').html(response);

            // Scroll to the #response div with smooth scroll
            $('html, body').animate({
                scrollTop: $('#response').offset().top
            }, 1000); // Scroll takes 1000ms (1 second)
        },
        error: function(xhr, status, error) {
            // Handle errors
            console.log("Error occurred:", error);
            $('#response').html('<p>Error fetching dojo data. Please try again later.</p>');
        }
        });
    });
    $('input[name="location"]').on('input', function() {
        hideError();
    });
});