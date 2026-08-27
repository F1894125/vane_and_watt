$(document).ready(function() {

    $('#register-form').on('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);

        const form = $(this);
        const registerUrl = form.data('register-url');
        const loginUrl = form.data('login-url');

        $('#register-error').hide();

        $.ajax({
            url: registerUrl,
            type: 'POST',
            contentType: false, // Tells jQuery not to manually set any content type header
            processData: false, // Prevents jQuery from automatically converting data to strings
            data: formData,
            success: function(response) {
                window.location.href = loginUrl;
            },
            error: function(xhr) {
                const errors = xhr.responseJSON;
                let allMessages = [];
                
                // To handle detail-based errors
                if (errors.detail) {
                    allMessages.push(errors.detail);
                }

                // To handle field-based errors
                else if (typeof errors === 'object') {
                    Object.entries(errors).forEach(([field, messages]) => {
                        if (Array.isArray(messages)) {
                            messages.forEach(message => {
                                console.error(`Field ${field}: ${message}`);
                                allMessages.push(`${message}`);
                            });
                        } else { // To handle single string errors in field-based errors
                            console.error(`Field ${field}: ${messages}`);
                            allMessages.push(`${messages}`);
                        }
                    });
                }
                showMessage(allMessages.join('\n'));
            }
        });
    });
});

function showMessage(message) {
    $('#register-error')
        .stop(true, true)
        .hide()
        .text(message)
        .fadeIn(300);
}