$(document).ready(function() {
    start()
    $('#table_paginator').on('click', 'a', function (e) {
        e.preventDefault();

        var link = $(this)

        $.ajax({
            type: 'get',
            url: link.attr('href'),
            dataType: 'json',
            success: function (response) {
                fill_table(response);
            },
            error: function(xhr, status, error) {
                console.log(xhr);
            }
        });
        set_paginate_pages
    })

    $('#register_form').submit(function (e) {
        e.preventDefault();

        var form = $(this);
        reset_validity_form(form);

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                form.find('[type="reset"]').click();
            },
            error: function(xhr, status, error) {
                set_validity_form(xhr, form);
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
        reset_validity_form(form);

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                form.find('[type="reset"]').click();
                location.reload();
            },
            error: function(xhr, status, error) {
                set_validity_form(xhr, form);
            }
        });
    });
});

function start() {
    $.ajax({
        type: 'get',
        url: '/api/comments/comments/?target_is_null=true',
        dataType: 'json',
        success: function (response) {
            fill_table(response)
        },
        error: function(xhr, status, error) {
            console.log(xhr);
        }
    });
}


function reset_validity_form(form) {
    form.find('input').each(function() {
        $(this).siblings('.invalid-feedback').text('');
        $(this).removeClass('is-invalid');
    });
    form.find('#form_errors').text('')
    form.find('#form_errors').addClass('d-none')
}

function set_validity_form(xhr, form) {
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

function fill_table(response) {
    var tbody = $('#comment_table').find('tbody')

    if (response && response.count != 0) {
        tbody.empty();
        for (let data of response.results) {
            add_table_row(data, tbody);
        }
        if (response.count > response.results.length) {
            $('#paginator_block').removeClass('d-none');
            set_paginate_pages(response);
        }
    } else {
        $('#empty_row').removeClass('d-none');
    }
}

function set_paginate_pages(response) {
    var current_page = response.current_page
    var total_pages = response.total_pages
    for (let link_name of ['first', 'previous', 'next', 'last']) {
            var link = $(`#${link_name}_page`)
            var url = response[link_name]
            if (url == null || new RegExp(`\\?page=${current_page}(?:&|$)`).test(url)) {
                link.addClass('disabled');
                link.attr('href', '#');
            } else {
                link.removeClass('disabled');
                link.attr('href', url);
            }
        }

    var pages
    if (current_page <= 3) {
        pages = [1, 2, 3, 4, 5];
    } else if (current_page >= total_pages - 2) {
        pages = [total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages];
    } else {
        pages = [current_page - 2, current_page -1, current_page, current_page + 1, current_page + 2];
    }

    var previous_li = $('#previous_page').parent();
    var next_li = $('#next_page').parent();
    previous_li.nextUntil(next_li).remove();

    for (let i of pages) {
        var extra_classes = ''
        if (i == response.current_page) {
            extra_classes = 'active'
        }
        next_li.before(`
            <li class="page-item"><a id="page_${i}" class="page-link ${extra_classes}" href="/api/comments/comments/?page=${i}&target_is_null=true">${i}</a></li>
        `)
    }
}
