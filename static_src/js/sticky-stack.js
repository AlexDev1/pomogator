// Sticky stack
// require vendor/jquery

// NOTE: не забудь где-то в стилях прописать
// .sticked { position: fixed }

/*
TODO:

* сделать проверку пересечений по x,
  чтобы была возможность делать несколько параллельных стопок (стеков)

*/

function stack(el, top_offset, top) {
    // если страница открылась на середине
    var saved_top = el.data("top");

    if (top_offset >= top) {
        el.css({top: saved_top});
        el.addClass("sticked");
    } else {
        el.css({top: ""});
        el.removeClass("sticked");
    }
}

(function($){
    $.fn.stickyStack = function(options) {
        var stick_stack_height = 0;

        this.each(function(){
            var self = $(this);

            // Запоминаем ширину блока
            var width = self.width();

            self.css({width: width});

            self.attr('data-top', stick_stack_height);

            if (self.attr('data-force-height') !== undefined) {
                stick_stack_height += parseInt(self.attr('data-force-height'));
            } else {
                stick_stack_height += self.height();
            }

            var self_top = self.offset().top;
            var top_offset = $(window).scrollTop() + parseInt(self.attr('data-top'));
            stack(self, top_offset, self_top);

            $(window).scroll(function(){
                var top_offset = $(window).scrollTop() + parseInt(self.attr('data-top'));

                stack(self, top_offset, self_top);
            });
        });
        return this;
    }
})(jQuery);

$(function(){
    $(".sticky-stack").stickyStack();
})
