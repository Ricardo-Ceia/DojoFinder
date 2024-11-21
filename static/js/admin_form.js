
//Review need of this code for error handling

/*$(document).ready(function() {  
    console.log("admin_form.js")
    $('.admin_form').on("submit",function(e){
        e.preventDefault();
        $.ajax({
            url: '/admin_login_form',
            method:'POST',
            data: $(this).serialize(),
            success:function(response){
                window.location.href = response['redirect'];
            }
            ,
            error: function(xhr, status, error) {
                // Add error handling
                console.error("Login error:", xhr.responseJSON);
                alert(xhr.responseJSON.error || "Login failed");
            }
    })
    })
})*/
