$(function(){
    // --- Back to top button ---
    // browser window scroll (in pixels) after which the "back to top" link is shown
    var offset = 200,
        // browser window scroll (in pixels) after which the "back to top" link opacity is reduced
        offset_opacity = 1000,
        // duration of the top scrolling animation (in ms)
        scroll_top_duration = 300,
        // grab the "back to top" link
        $back_to_top = $('#back-to-top');

    // hide or show the "back to top" link
    $(window).scroll(function(){
        ( $(this).scrollTop() > offset ) ? $back_to_top.addClass('visible') : $back_to_top.removeClass('visible fade-out');
        if( $(this).scrollTop() > offset_opacity ) {
            $back_to_top.addClass('fade-out');
        }
    });

    // smooth scroll to top
    $back_to_top.on('click', function(event){
        event.preventDefault();
        $('body,html').animate({
            scrollTop: 0 ,
            }, scroll_top_duration
        );
    });
});
