function start_socket () {
    socket = new WebSocket('/api/ws/comments/');
    socket.onmessage = function(e) {
        start();
    };

    socket.onopen = function(e) {
        console.log("WebSocket is open now.");
    };

    socket.onclose = function(e) {
        console.log("WebSocket is closed now.");
    };
}

$(document).ready(function() {
    start();
    start_socket();
    $('tr a[id$=_col]').click(function (e) {
        e.preventDefault();

        var active_page = $('[id^=page].active');
        var link = $(this);
        var link_id = link.attr('id');
        var link_sort = link.attr('data-sort')
        var url = `${active_page.attr('href')}&ordering=`
        console.log(url)
        if (link_id.includes('email')) {
            url += `${link_sort}email`
        } else if (link_id.includes('username')) {
            url += `${link_sort}username`
        } else if (link_id.includes('updated')) {
            url += `${link_sort}updated`
        } else if (link_id.includes('created')) {
            url += `${link_sort}created`
        }
        console.log(url)


        $.ajax({
            type: 'get',
            url: url,
            success: function (response) {
                console.log(response);
                fill_table(response);
            }
        })

        if (link_sort == '-') {
            link.attr('data-sort', '');
        } else {
            link.attr('data-sort', '-');
        }

    });

    $(document).on('click', 'a[name="edit"]', function(e) {
        var link = $(this);
        var comment = $(`#comment_detail_${link.attr('data-target-id')}`)
        var form = $('#editor_form');
        reset_validity_form(form);
        form.attr('method', 'patch');
        form.attr('action', link.attr('href'));
        form.find('h1').text('Edit');
        form.find('#text_editor div[contenteditable="true"]').html(comment.find('div.card-text').first().html());
        form.find('button[type="submit"]').text('Save');
    });

    $(document).on('click', 'a[name="remove"]', function(e) {
        e.preventDefault();

        var link = $(this)

        $.ajax({
            type: 'delete',
            url: link.attr('href'),
            headers: {'X-CSRFToken': Cookies.get('csrftoken')},
            success: function (response) {
                if ($(`#comment_table tbody tr[id="${link.attr('data-target-id')}"]`).length == 1) {
                    $('#return').click();
                    start();
                } else {
                    var comment = $(`#comment_detail_${link.attr('data-target-id')}[data-comment-type="answer"]`)
                    var answer_block = comment.parent();
                    var parent_comment = answer_block.parent();
                    comment.remove();
                    answer_block.empty();
                    show_comment_answers(parent_comment);
                }
            }

        });
    });

    $(document).on('click', 'a[name="answer"]', function(e) {
        var link = $(this)
        var form = $('#editor_form');
        clear_editor_form();
        reset_validity_form(form);
        form.attr('method', 'post');
        form.attr('action', 'api/comments/comments/');
        form.find('h1').text('Create New Answer');
        form.find('button[type="submit"]').text('Answer');
        form.find('#target_field').attr('value', link.attr('data-target-id'));
    });

    $('#nav_create_comment').click(function (e) {
        var form = $('#editor_form');
        clear_editor_form();
        reset_validity_form(form);
        form.attr('method', 'post');
        form.attr('action', 'api/comments/comments/');
        form.find('h1').text('Create New Comment');
        form.find('button[type="submit"]').text('Publish');
    });

    $('#editor_form button[type="reset"]').click(function (e) {
        clear_editor_form();
    });

    $('#editor_form').submit(function (e) {
        e.preventDefault();

        var form = $(this);
        reset_validity_form(form);
        var target_id = form.find('#target_field').val();
        var show_answers_link = $(`#comment_detail_${target_id} a[name="show_answers"]`)
        var answer_block = $(`#answer_block_${target_id}`)
        var submit_button = form.find('button[type="submit"]');


        var text_field_value = form.find('#text_editor div[contenteditable="true"]').html();
        if (text_field_value != '<p><br></p>') {
            form.find('#text_field').val(text_field_value);
        }

        var form_data = new FormData(form[0])
        for (let pair of form_data.entries()) {
            if (pair[1] instanceof File && pair[1].size === 0) {
                form_data.delete(pair[0]);
            }
        }

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form_data,
            processData: false,
            contentType: false,
            headers: {'X-CSRFToken': Cookies.get('csrftoken')},
            success: function (response) {
                form.find('[type="reset"]').click();

                if (submit_button.text().includes('Save')) {
                    var commend_id = form.attr('action').split('/')[3]
                    if ($(`#${commend_id}`)) {
                        $('#table_paginator a.active').click();
                    }
                    var comment = $(`#comment_detail_${commend_id}`);
                    var media =  comment.find(`#media_${commend_id}`)
                    comment.find('div.card-text').first().html(response.text);
                    media.empty();
                    if (response.image) {
                        media.prepend(get_image_link_template(response));
                        lightbox.init();
                    }
                    if (response.file) {
                        media.append(get_file_link_template(response))
                    }
                }

                if (show_answers_link.attr('aria-expanded') === 'false') {
                    answer_block.addClass('show');
                    show_answers_link.attr('aria-expanded', 'true');
                    show_answers_link.click();
                } else {
                    if (submit_button.text().includes('Answer')) {
                        add_comment_to_element(answer_block, response, comment_type='answer', prepend=true)
                    }

                    var answer_block_children = answer_block.children().not(':last')
                    if (answer_block_children.length >= 25) {
                            answer_block_children.last().remove();
                    }
                }

            },
            error: function(xhr, status, error) {
                set_validity_form(xhr, form);
            }
        });
    });

    $(document).on('click', 'a[name="show_answers"]', function(e){
        var link = $(this);
        var target = $(`#main_comment_block #comment_detail_${link.attr('data-target-id')}`);
        if (link.attr('aria-expanded') == 'true') {
            show_comment_answers(target);
        } else {
            var answer_block = target.find(`#answer_block_${target.attr('data-comment-id')}`);
            answer_block.empty();
        }

    });

    $(document).on('click', '[id^="show_comments_yet"]', function(e) {
        e.preventDefault();
        let link = $(this);
        let target = $(link.attr('data-target-id'));
        show_comment_answers(target, link.attr('href'));
        link.remove();
    });

    $('#comment_table').on('click', 'a[name="read"]', function(e) {
        e.preventDefault();

        let link = $(this);

        $.ajax({
            type: 'get',
            url: link.attr('href'),
            dataType: 'json',
            success: function (response) {
                hide_table();
                create_return_button();
                show_comment_detail(response);
            },
            error: function(xhr, status, error) {
                console.log(xhr);
            }
        });

    });

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
    const quill = new Quill('#text_editor', {
        theme: 'snow',
        modules: {
          toolbar: [
            ['bold', 'italic', 'underline', 'strike'],
            ['code', 'link'],
          ]
        }
    });
});

function clear_editor_form(form) {
    var form = $('#editor_form');
    form.find('#text_editor div[contenteditable="true"]').html('<p><br></p>');
    form.find('#text_field').val('');
    form.find('#image_field').val('');
    form.find('#file_field').val('');
}

function start() {
    $.ajax({
        type: 'get',
        url: '/api/comments/comments/?target_is_null=true',
        dataType: 'json',
        success: function (response) {
            fill_table(response);
        },
        error: function(xhr, status, error) {
            console.log(xhr);
        }
    });
}

function show_comment_answers(target, next_page_url=undefined) {
    let url
    if (next_page_url) {
        url = next_page_url
    } else {
        url = `api/comments/comments/?target=${target.attr('data-comment-id')}`
    }

    var answer_block = target.find(`#answer_block_${target.attr('data-comment-id')}`)

    $.ajax({
        type: 'get',
        url: url,
        dataType: 'json',
        success: function (response) {
            if (response.results) {
                for (answer_data of response.results) {
                    add_comment_to_element(answer_block, answer_data, comment_type='answer');
                }
                if (response.next) {
                    create_show_comments_yet_link(target, response.next);
                }
            }
        }
    })
}

function show_comment_detail(data) {
    add_comment_to_element($('#main_comment_block'), data, 'main_comment');
    main_comment = $('#main_comment_block [data-comment-type="main_comment"]');
    show_comment_answers(main_comment);
};

function create_return_button() {
    $('#main_comment_block').append(`
        <button id='return' type="button" class="btn btn-primary mb-3" onclick="on_return_button()">Return</button>
    `);

}

function on_return_button() {
    $('#main_comment_block').empty();
    show_table();
}

function create_show_comments_yet_link(target, next_page_url) {
    target.find(`#answer_block_${target.attr('data-comment-id')}`).append(`
        <div class="d-flex justify-content-center">
            <a id="show_comments_yet_${target.attr('data-comment-id')}" class="link-secondary" data-target-id="#${target.attr('id')}" href="${next_page_url}">Show Yet Comments</a>
        </div>
    `)
}

function create_comment_template(data, comment_type) {
    var owner_links = '';
    if ($('#nav_user_menu').text().includes(data.user.email)) {
        owner_links = `
            <a name="edit" role="button" href="api/comments/comments/${data.uuid}/" class="card-link text-decoration-none" data-target-id="${data.uuid}" data-bs-toggle="modal" data-bs-target="#editor_modal">
                ${feather.icons['edit'].toSvg({class: 'icon-size-20'})}
            </a>
            <a name="remove" role="button" href="api/comments/comments/${data.uuid}/" class="card-link text-decoration-none" data-target-id="${data.uuid}">
                ${feather.icons['trash-2'].toSvg({class: 'icon-size-20'})}
            </a>
        `
    }

    var image_link = '';
    if (data.image) {
        image_link = get_image_link_template(data);
    }

    var file_link = '';
    if (data.file) {
        file_link = get_file_link_template(data);
    }

    var show_class = '';
    var aria_expanded = 'false'
    if (comment_type.includes('main_comment')) {
        show_class = 'show'
        aria_expanded = 'true'
    }
    var not_owner_links = `
        <a name="answer" role="button" class="card-link text-decoration-none" data-target-id="${data.uuid}" data-bs-toggle="modal" data-bs-target="#editor_modal">
            Answer
        </a>
        <a name="show_answers" role="button" class="card-link text-decoration-none" data-bs-toggle="collapse" href="#answer_block_${data.uuid}" data-target-id="${data.uuid}" aria-expanded="${aria_expanded}">
            ${feather.icons['message-square'].toSvg({class: 'icon-size-20'})}
        </a>
    `

    let template = `
        <div id="comment_detail_${data.uuid}" data-comment-id="${data.uuid}" data-comment-type=${comment_type}>
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between">
                    <h6 class="text-primary-emphasis">${data.user.username} | ${data.user.email}</h6>
                    <h6 class="text-primary-emphasis">
                        Updated: ${format_date(data.updated)} ${format_time(data.updated)} |
                        Created: ${format_date(data.created)} ${format_time(data.created)}
                    </h6>
                </div>
                <div class="card-body">
                    <div class="card-text">${data.text}</div>
                    <div id="media_${data.uuid}" class="d-flex flex-row">
                        ${image_link}
                        ${file_link}
                    </div>
                </div>
                <div class="card-footer">
                    ${not_owner_links}
                    ${owner_links}
                </div>
            </div>
          <div id="answer_block_${data.uuid}" class='ps-5 collapse ${show_class}'></div>
        </div>
    `
    return template
}

function get_image_link_template(data) {
    return `
            <a id="image" href="${data.image}" data-lightbox="${data.uuid}" class="me-2">
                <img src="${data.image}" class='img-thumbnail' style="width: 60px;">
            </a>
        `
}

function get_file_link_template(data) {
    return `
            <a id="file" href="${data.file}" download>
                ${feather.icons['file-text'].toSvg({style: "width: 40px; height: 40px;"})}
            </a>
        `
}

function add_comment_to_element(element, data, comment_type, prepend=false) {
    let comment = create_comment_template(data, comment_type);
    if (prepend) {
        element.prepend(comment);
    } else {
        element.append(comment);
    }

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

function fill_table(response) {
    var tbody = $('#comment_table').find('tbody')
    if (response) {
        tbody.empty();
        for (let data of response.results) {
            add_table_row(data, tbody);
        }
        if (response.count > response.results.length) {
            $('#paginator_block').removeClass('d-none');
            console.log('set_paginator', response)
            set_paginate_pages(response);
        }
    } else {
        $('#empty_row').removeClass('d-none');
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

function set_paginate_pages(response) {
    var current_page = response.current_page
    var total_pages = response.total_pages
    for (let link_name of ['first', 'previous', 'next', 'last']) {
            var link = $(`#${link_name}_page`)
            var url = response[link_name]
            if (url == null || new RegExp(`page=${current_page}(?:&|$)`).test(url)) {
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
        regex = /page=1(?=&|$)/;
        var href = response.first.replace(regex, `page=${i}`)
        next_li.before(`
            <li class="page-item"><a id="page_${i}" class="page-link ${extra_classes}" href="${href}">${i}</a></li>
        `)
    }
}

function hide_table() {
    $('#table_block').hide();
}

function show_table() {
    $('#table_block').show();
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
