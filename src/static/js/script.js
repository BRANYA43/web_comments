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

function format_date(iso_datetime) {
    let datetime = new Date(iso_datetime);
    let day = String(datetime.getDate()).padStart(2, '0');
    let month = String(datetime.getMonth()).padStart(2, '0');
    let year = datetime.getFullYear();
    return `${day}.${month}.${year}`
}

function format_time(iso_datetime) {
    let datetime = new Date(iso_datetime);
    let hours = String(datetime.getHours()).padStart(2, '0');
    let minutes = String(datetime.getMinutes()).padStart(2, '0');
    let seconds = String(datetime.getSeconds()).padStart(2, '0');
    return `[${hours}:${minutes}:${seconds}]`;
}

function add_table_row(data, tbody) {
    tbody.append(`
        <tr id="${data.uuid}" class="align-middle" style="height: 90px;">
        <td>${data.user.email}</td>
        <td>${data.user.username}</td>
        <td class="w-100"><div class="text-truncate-multiline">${data.text}</div></td>
        <td>${format_date(data.updated)}<br>${format_time(data.updated)}</td>
        <td>${format_date(data.created)}<br>${format_time(data.created)}</td>
        <td>
            <div class="d-flex flex-column">
            <a name="read" class="text-decoration-none align-self-center" href="/api/comments/comments/${data.uuid}/">
                ${feather.icons['book-open'].toSvg()}
            </a>
            </div>
        </td>
        </tr>
    `);
}

function fill_table() {
    console.log('run fill table')
    var tbody = $('#comment_table').find('tbody')
    $.ajax({
        type: 'get',
        url: '/api/comments/comments/?target_is_null=true',
        dataType: 'json',
        success: function (response) {
            console.log(response);
            if (response && response.count != 0) {
                for (let data of response.results) {
                    add_table_row(data, tbody);
                }
            } else {
                console.log('show empty row');
                $('#empty_row').removeClass('d-none');
            }
        },
        error: function(xhr, status, error) {
            console.log(xhr)
        }
    });
}

$(document).ready(function() {
    fill_table()

    $('#register_form').submit(function (e) {
        e.preventDefault();

        var form = $(this);
        clean_validated_form(form);

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                form.find('[type="reset"]').click();
            },
            error: function(xhr, status, error) {
                set_invalid_feedback(xhr, form);
            }
        });
    });

    $('#nav_logout').click(function (e) {
        e.preventDefault();

        var link = $(this)

        $.ajax({
            type: 'get',
            url: link.attr('href'),
            success: function (response) {
                location.reload();
            },
        });
    });

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
