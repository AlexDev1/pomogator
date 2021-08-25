// Requires static/js/lib.js

$(function(){
    // Common
    var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ? true : false;

    // fix branding position
    var screen_width = $("body").width();
    var main_width = $("#main").css("width");
    var main_width_inner = $("#main").width();

    $(".slider").tp_slider();


    // open popup from hash
    var thisHash = window.location.hash;
    if (thisHash && $(thisHash).hasClass("popup")) {
        $(thisHash).tp_dialog('open');
    }
    make_openpopups();

    // Ajax forms
    $("form.ajax").ajaxForm(ajaxFormOptions);


    // custom scroll buttons
    $(".scroll-left").click(function() {
        var target = $($(this).data('target'));
        var left = target.scrollLeft();
        target.animate({scrollLeft: left - 134}, 200);
    });

    $(".scroll-right").click(function() {
        var target = $($(this).data('target'));
        var left = target.scrollLeft();
        target.animate({scrollLeft: left + 134}, 200);
    });


    // Hamburger open popup menu
    if (isMobile) {
        var animation_speed = 0;
    } else {
        var animation_speed = 300;
    }

    var menu_popup = $("#main-menu-popup");
    var menu = menu_popup.find(".main-menu-wrap");
    var menu_width = menu.width();
    var main_block = $("#main, header, footer");

    $("#main-menu-popup .overlay, .main-menu-wrap > .close").on("click", function(){
        $("#main-menu-popup .overlay").fadeOut(animation_speed);
        menu.removeClass("active");
        main_block.animate({left: 0}, animation_speed);
        // $(".sticky-menu .menu").animate({left: 0}, animation_speed);
        $("body").css({"overflow-x": "visible"});
    });

    $("#hamburger").on("click", function(){
        $("#main-menu-popup").fadeIn(animation_speed);
        $("#main-menu-popup .overlay").fadeIn(animation_speed);

        menu.addClass("active");
        // нужно ли двигать основной блок
        if (main_block.offset().left <= menu_width) {
            var main_block_offset = (menu_width - main_block.offset().left);
            main_block.animate({left: main_block_offset}, animation_speed);
        }

        // $(".sticky-menu .menu").animate({left: 0}, animation_speed);
        $("body").css({"overflow-x": "hidden"});
    });

    // Treemenus in left menu
    // $("#main-menu-popup .menu").treemenu({
    //     'delay': animation_speed,
    //     'activeSelector': '.active',
    //     // 'closeOther': true
    //      'openActive': true
    // });

    make_spoilers();

    $(".close").click(function(){
        var target = $(this).data('target');
        $(target).slideUp(300);
        $("[data-target='" + target + "']").removeClass("active");
    });

    // Topic - carousel
    $('#topics-carousel-main').slick({
    centerMode: false,
    centerPadding: '0px',
    infinite: false,
    slidesToShow: 2.75,
    nextArrow: '<button class="owl-next"><i class="fa fa-long-arrow-right" aria-hidden="true"></i></button>',
    prevArrow: '<button class="owl-prev"><i class="fa fa-long-arrow-left" aria-hidden="true"></i></button>',
    responsive: [
      {
        breakpoint: 768,
        settings: {
          arrows: true,
          centerMode: false,
          centerPadding: '0px',
          slidesToShow: 2.4
        }
      },
      {
        breakpoint: 480,
        settings: {
          arrows: true,
          centerMode: false,
          centerPadding: '0px',
          slidesToShow: 2.3
        }
      }
    ]
  });
    $('#topics-carousel').slick({
    centerMode: false,
    centerPadding: '0px',
    infinite: false,
    slidesToShow: 4.75,
    nextArrow: '<button class="owl-next"><i class="fa fa-long-arrow-right" aria-hidden="true"></i></button>',
    prevArrow: '<button class="owl-prev"><i class="fa fa-long-arrow-left" aria-hidden="true"></i></button>',
    responsive: [
      {
        breakpoint: 768,
        settings: {
          arrows: true,
          centerMode: false,
          centerPadding: '0px',
          slidesToShow: 2.4
        }
      },
      {
        breakpoint: 480,
        settings: {
          arrows: true,
          centerMode: false,
          centerPadding: '0px',
          slidesToShow: 2.3
        }
      }
    ]
  });

});
