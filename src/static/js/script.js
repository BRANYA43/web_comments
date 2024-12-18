function clean_validated_form(form) {
    form.find('input').each(function() {
        $(this).siblings('.invalid-feedback').text('');
        $(this).removeClass('is-invalid');
    });
    form.find('#form_errors').text('')
    form.find('#form_errors').addClass('d-none')
}

function set_invalid_feedback(xhr, form) {
    if (xhr.responseJSON && xhr.responseJSON.errors) {
        xhr.responseJSON.errors.forEach(function(error) {
            var field_name = error.attr;
            var detail = error.detail;
            if (field_name) {
                var field = form.find(`[name="${field_name}"]`);
                field.addClass('is-invalid');
                field.siblings('.invalid-feedback').text(detail);
            } else {
                form.find('#form_errors').show().text(detail);
                form.find('#form_errors').removeClass('d-none');
            }
        });
    }
}

$(document).ready(function() {
    $('#login_form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        clean_validated_form(form);

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                form.find('[type="reset"]').click();
                location.reload();
            },
            error: function(xhr, status, error) {
                set_invalid_feedback(xhr, form);
            }
        });
    });
});
