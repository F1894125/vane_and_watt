$(document).ready(function() {
    const editProfileForm = $('#edit-profile-form');
    
    const initialValues = {
        username: $('#id_username').val(),
        email: $('#id_email').val(),
        first_name: $('#id_first_name').val(),
        last_name: $('#id_last_name').val(),
        date_of_birth: $('#id_date_of_birth').val(),
        photo: $('#id_photo').val(),
    }

    editProfileForm.on('submit', function(e) {
        e.preventDefault();

        const payload = new FormData();

        // Only sending changed fields
        editProfileForm.find('input, select, textarea').each(function() {
            const fieldName = this.name;
            if (!fieldName)
                return;

            if (this.type === 'file') {
                if (this.files && this.files.length > 0) {
                    payload.append(fieldName, this.files[0]);
                }
                return;
            }

            const currentValue = this.value

            if (initialValues[fieldName] !== currentValue) {
                payload.append(fieldName, currentValue);
            }
        });
        
        const updateUrl = editProfileForm.data('update-url');

        $('#profile-error').hide();

        // Printing the payload values in the console
        console.log('Profile update payload:\n');
        payload.forEach((value, key) => {
            console.log(`${key}: ${value}`);
        });

        $.ajax({
            url: updateUrl,
            type: 'PATCH',
            data: payload,
            contentType: false,
            processData: false,
            success: function(response) {
                window.location.reload();
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
    $('#profile-error')
        .stop(true, true)
        .hide()
        .text(message)
        .fadeIn(300);
}