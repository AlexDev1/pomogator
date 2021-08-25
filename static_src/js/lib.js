/* Requires:
  "{{ STATIC_URL }}vendor/magnific-popup/dist/jquery.magnific-popup.min.js"
  "{{ STATIC_URL }}vendor/jquery-form/jquery.form.js"
*/


function createElement(elName, attrs) {
    /* Example:
        var myDiv = createElement("div", {className: "my-div"});
    */

    var newElement = document.createElement(elName);

    for (var k in attrs) {
        newElement[k] = attrs[k];
    }

    return newElement;
}

function hasClass(el, className) {
    return (el.className.indexOf(className) > -1) ? true: false;
}

function addClass(el, className) {
    if (el.className.length) {
        el.className = el.className + " " + className;
    } else {
        el.className = className;
    }
}

function removeClass(el, className) {
    var _className = className;

    var class_list = el.className.split(" ").filter(function(el, idx, arr) {
        if (el !== _className) {
            return el
        }
    });

    el.className = class_list.join(" ");
}

function objectToUrlParams(dict, encodeURI) {

  let urlParams = '?';
  for(var key in dict) {
    if (urlParams !== '?') {
      urlParams += '&';
    }

    let val = dict[key]
    if (encodeURI) {
      val = encodeURIComponent(val);
    }

    urlParams += `${key}=${val}`;
  }

  return urlParams;
}

function HTMLCollectionForEach(html_collection, func) {
    for(var i=0; i < html_collection.length; i++) {
        func(html_collection[i]);
    }
}

function sendAjax(options) {
    var xhr = new XMLHttpRequest();

    options.url = options.url || '';
    options.method = options.method || 'GET';
    options.success = options.success || function(responseText) { console.log(responseText) };
    options.fail = options.success || function(responseText) { console.log(status, statusText) };


    // 2. Конфигурируем его: GET-запрос на URL 'phones.json'
    xhr.open(options.method, options.url, false);

    // 3. Отсылаем запрос
    xhr.send();

    // 4. Если код ответа сервера не 200, то это ошибка
    if (xhr.status != 200) {
        options.fail(xhr.status, xhr.statusText);
    } else {
        options.success(xhr.responseText);
    }
}

// Default options
var ajaxFormOptions = {
    beforeSerialize: function($form, options) {
        if (typeof CKEDITOR !== 'undefined') {
            console.log("CKEDITOR defined");
            for(instance in CKEDITOR.instances) {
                CKEDITOR.instances[instance].updateElement();
            }
        }
    },
    success: function(responseText, statusText, xhr, $form) {
        if(responseText.success == true) {
            console.info("Form data submitted");

            if (responseText.reload == true) {
                location.reload();
            }

            if (responseText.show_message == true) {
                $($form).siblings(".message").text(responseText.message);
                $($form).hide(200);
            } else {
                $.magnificPopup.close();
            }
        } else if (responseText.form_invalid == true) {
            $($form).find(".error").detach();

            for (var key in responseText.form_errors) {
                var el = $($form).find("#id_" + key);
                var el_err = responseText.form_errors[key][0];

                var err_block = $("id_error_" + el.attr("id"));
                if (!err_block.length) {
                    var err_block = $("<div>");
                    err_block.attr("id", "id_error_" + el.attr("id"));
                    err_block.addClass("error")
                }

                err_block.text(el_err);
                el.before(err_block);
            }
        } else {
            console.info('ajax form response:', responseText.message);
            $($form).siblings(".errors").text(responseText.message);
        }
    }
};

var magnificPopupDefaultOptions = {
    type: 'inline',
    showCloseBtn: true,
    callbacks: {
        beforeClose: function() {
            // Remove hash from url
            history.pushState('', document.title, window.location.pathname);
        },
        open: function() {
            // fix scroll
            $('html').css({
                "margin-right": 0,
                "overflow": "visible"
            });
        }
    }
};


// jQuery function
// "tp_" is tourprom prefix
(function($){
    $.fn.tp_slider = function(options) {
        /* Обёртка для слайдера
           позволяет задавать опции слайдера в data-атрибутах тега
           Пример:
           <div class="slider" data-autoplay="false">...</div>

           $('.slider').tp_slider();
        */
        this.each(function(){
            var options = $(this).data();
            $(this).unslider(options);
        });
        return this;
    }
})(jQuery);


(function($){
    var methods = {
        init: function() {},
        open: function(options) {
            /* Открывает диалог из указанного элемента
               Пример:

               <div id="popup">Всплывающее окно</div>
               ...
               $("#popup").tp_dialog_open();
            */
            var options = magnificPopupDefaultOptions;
            options['items'] = {
                src: $(this)
            };

            $.magnificPopup.open(options);

            // Ajax forms
             $("form.ajax").ajaxForm(ajaxFormOptions);
        },
        close: function(options) {
            $.magnificPopup.close();
        },
        button: function(options) {
            /* Создаёт активатор модального окна из элемента.
                Кнопка открывает модальное окно созданное из элемента указанного
                в data-target или href (у ссылки)
                В data-target/href должен быть селектор

                Пример:
                <div class="lets-popup" data-target="#popup">Кнопка, открывающая модальное окно</div>
                <a class="lets-popup" href="#popup">Другая кнопка, открывающая модальное окно</a>
                ...
                <div id="popup">Я модальное окно</div>

                $(".lets-popup").tp_popup();
            */

            var default_options = magnificPopupDefaultOptions;

            this.each(function(e){
                $.extend(default_options, $(this).data());
                $.extend(default_options, options);

                var target = "";
                if ($(this).prop("tagName") == 'A') {
                    target = $(this).attr("href");
                } else {
                    target = $(this).data("target");
                }

                default_options['items'] = {
                    src: target
                };

                $(this).on("click", function(){
                    $(target).tp_dialog('open', default_options); //magnificPopup(default_options);
                });

                // Ajax forms
                $("form.ajax").ajaxForm(ajaxFormOptions);
            });

            return this;
        }
    };

    $.fn.tp_dialog = function(method) {
        // Логика вызова метода
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Метод ' +  method + ' не существует в jQuery.tp_dialog' );
        }
    };
})(jQuery);


function tp_stick_menu(el, top_offset) {
    if( $(window).scrollTop() > top_offset ) {
        $(el).addClass("sticky-menu");
    } else {
        $(el).removeClass("sticky-menu");
    }
}

function make_spoilers() {
    $(".spoiler").click(
        function(e) {
            var target = $(this).data('target');
            if ($(this)[0].hasAttribute("data-close")) {
                var close_target = $(this).attr('data-close').split(" ");
            }
            $(target).slideToggle(500);
            $(this).toggleClass("active");
            // console.log(close_target.length);
            for(var i=0; i < close_target.length; i++) {
                // console.log(close_target[i]);
                $(close_target[i]).slideUp(100);
                $("[data-target='"+close_target[i]+"']").removeClass("active");
            };
        }
    );
}

function make_openpopups() {
    $(".open-popup").tp_dialog('button');

    $(".open-ajax-popup").magnificPopup({
        'type': "ajax",
    });

    $(".open-iframe-popup").magnificPopup({
        type: "iframe",
        markup: '<div class="a mfp-iframe-scaler">'+
            '<div class="mfp-close"></div>'+
            '<iframe class="mfp-iframe" frameborder="0" allowfullscreen></iframe>'+
          '</div>', // HTML markup of popup, `mfp-close` will be replaced by the close button

    });

    $(".close-popup").on("click", function(){
        $(this).tp_dialog('close');
    });
}


// OLD CODE FROM media/js/main.js:203
function strip_html(html) {
    //
    var tmp = document.createElement("DIV");
    tmp.innerHTML = html;
    return tmp.textContent||tmp.innerText;
}

function linebreaks_2_p(text) {
    var ps = text.split("\n");
    var html = '';
    for(var i=0; i<ps.length; i++)
        if(ps[i].length)
            html += '<p>' + ps[i] + '</p>\n';
    return html;
}

function is_valid_url(url){
     return url.match(/^(https?:\/\/)?[a-zа-я0-9-\.]+\.[a-zа-я]{2,4}\/?([^\s<>\#%"\,\{\}\\|\\\^\[\]`]+)?$/);
}
