$(document).ready(function() {

    // Domain Switcher Handler
    $('input[name="domain_selector"]').on('change', function() {
        $('#prediction-message').hide();

        if ($('#btn-weather').is(':checked')) {
            $('#weather-form').fadeIn(200);
            $('#energy-form').hide();
        } else {
            $('#weather-form').hide();
            $('#energy-form').fadeIn(200);
        }
    });

    // Helper function to parse comma-separated text into arrays for ArrayFields
    function parseArrayInput(val, isInt = false) {
        if (!val || typeof val !== 'string')
            return [];
        
        return val.split(',').map(item => {
            let trimmed = item.trim();
            return isInt ? parseInt(trimmed, 10) : parseFloat(trimmed);
        });
    }

    // Weather Form Submission
    $('#weather-form').on('submit', function(e) {
        e.preventDefault();

        const form = $(this);
        const predictUrl = form.data('predict-url');

        const payload = {
            precipitation_mm: parseArrayInput($('#id_precipitation_mm').val()),
            is_weekend: parseArrayInput($('#id_is_weekend').val(), true),
            is_raining: parseArrayInput($('#id_is_raining').val(), true),
            sin_day_of_year: parseArrayInput($('#id_sin_day_of_year').val()),
            cos_day_of_year: parseArrayInput($('#id_cos_day_of_year').val()),
            sin_month: parseArrayInput($('#id_sin_month').val()),
            cos_month: parseArrayInput($('#id_cos_month').val()),
            sin_wind_dir: parseArrayInput($('#id_sin_wind_dir').val()),
            cos_wind_dir: parseArrayInput($('#id_cos_wind_dir').val()),
            avg_temp_c: parseArrayInput($('#id_avg_temp_c').val()),
            min_temp_c: parseArrayInput($('#id_min_temp_c').val()),
            max_temp_c: parseArrayInput($('#id_max_temp_c').val()),
            avg_sea_level_pres_hpa: parseArrayInput($('#id_avg_sea_level_pres_hpa').val()),
            avg_wind_speed_kmh: parseArrayInput($('#id_avg_wind_speed_kmh').val())
        };

        submitPrediction(predictUrl, payload, form, 'weather');
    });

    // Energy Form Submission
    $('#energy-form').on('submit', function(e) {
        e.preventDefault();

        const form = $(this);
        const predictUrl = form.data('predict-url');

        const payload = {
            category: $('input[name="category"]:checked').val(),
            hour: parseInt($('#id_hour').val(), 10),
            day: parseInt($('#id_day').val(), 10),
            month: parseInt($('#id_month').val(), 10),
            dayofweek: parseInt($('#id_dayofweek').val(), 10),
            lag_1: parseFloat($('#id_lag_1').val()),
            lag_24: parseFloat($('#id_lag_24').val())
        };

        submitPrediction(predictUrl, payload, form, 'energy');
    });

    // Unified AJAX Submission Handler
    function submitPrediction(url, payload, form, domain) {
        $('#prediction-message').hide();

        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function(response) {
                showMessage(
                    response.message || 'Prediction task dispatched successfully!',
                    'success'
                );
                form[0].reset();
                setTimeout(() => {
                    window.location.href = `/forecasting/api/history/${domain}/${response.id}`;
                }, 3000);
            },
            error: function(xhr) {
                const errors = xhr.responseJSON;
                let allMessages = [];

                if (!errors) {
                    allMessages.push('An unexpected error occurred. Please check your inputs.');
                } else if (errors.detail) {
                    allMessages.push(errors.detail);
                } else if (typeof errors === 'object') {
                    Object.entries(errors).forEach(([field, messages]) => {
                        if (Array.isArray(messages)) {
                            messages.forEach(message => {
                                console.error(`Field ${field}: ${message}`);
                                allMessages.push(`${field}: ${message}`);
                            });
                        } else {
                            console.error(`Field ${field}: ${messages}`);
                            allMessages.push(`${field}: ${messages}`);
                        }
                    });
                }

                showMessage(allMessages.join('\n'), 'danger');
            }
        });
    }

    function showMessage(message, type) {
        if (type === 'success') {
            $('#prediction-message')
                .removeClass('alert alert-danger')
                .addClass('alert alert-success');
        } else {
            $('#prediction-message')
                .removeClass('alert alert-success mt-3')
                .addClass('alert alert-danger mt-3');
        }
        $('#prediction-message')
            .stop(true, true)
            .hide()
            .text(message)
            .fadeIn(300);
    }
});