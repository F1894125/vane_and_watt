$(document).ready(function() {

    $('#login-form').on('submit', function(e) {
        e.preventDefault();

        const form = $(this);
        const loginUrl = form.data('login-url');
        const dashboardUrl = form.data('dashboard-url');

        const payload = {
            username: $('#id_username').val(),
            password: $('#id_password').val()
        };

        $('#login-error').hide();

        $.ajax({
            url: loginUrl,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function(response) {
                //alert(response.detail);
                window.location.href = dashboardUrl;
            },
            error: function(xhr) {
                const errors = xhr.responseJSON;
                let allMessages = [];
                
                if (errors.detail) {
                    allMessages.push(errors.detail);
                }
                else if (typeof errors === 'object') {
                    Object.entries(errors).forEach(([field, messages]) => {
                        if (Array.isArray(messages)) {
                            messages.forEach(message => {
                                console.error(`Field ${field}: ${message}`);
                                allMessages.push(`${message}`);
                            });
                        } else {
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
    $('#login-error')
        .stop(true, true)
        .hide()
        .text(message)
        .fadeIn(300);
}