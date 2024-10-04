/**
 *
 * --------------------------------------------------------------------
 *
 * Template : Custom Js Template
 * Author : reacthemes
 * Author URI : http://www.reactheme.com/
 *
 * --------------------------------------------------------------------
 *
 **/
(function ($) {
    "use strict";

    $(document).ready(function () {
        $('[data-toggle="tooltip"]').tooltip();
    });


    var swiper = new Swiper(".university__slider__thumb", {
        spaceBetween: 10,
        slidesPerView: 4,
        freeMode: true,
        watchSlidesProgress: true,
    });

    var swiper2 = new Swiper(".university__slider", {
        spaceBetween: 10,
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        thumbs: {
            swiper: swiper,
        },
    });

    var swiper = new Swiper(".ecommerce__slider", {
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        grabCursor: true,
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        slidesPerView: 1,
    });

    var swiper = new Swiper(".ai__slider", {
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        grabCursor: true,
        slidesPerView: 1,
    });

    var swiper = new Swiper(".featured__course", {
        grabCursor: true,
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        slidesPerView: 1,
        breakpoints: {
            575: {
                slidesPerView: 2,
            },

            768: {
                slidesPerView: 2,
            },

            992: {
                slidesPerView: 3,
            },
            1200: {
                slidesPerView: 3
            },
            1500: {
                slidesPerView: 4
            }
        },
    });



    $.fn.skillBars = function (options) {
        var settings = $.extend({
            from: 0, // number start
            to: false, // number end
            speed: 1000, // how long it should take to count between the target numbers
            interval: 100, // how often the element should be updated
            decimals: 0, // the number of decimal places to show
            onUpdate: null, // callback method for every time the element is updated,
            onComplete: null, // callback method for when the element finishes updating
            /*onComplete: function(from) {
                console.debug(this);
            }*/
            classes: {
                skillBarBar: '.skillbar-bar',
                skillBarPercent: '.skill-bar-percent',
            }
        }, options);

        return this.each(function () {

            var obj = $(this),
                to = (settings.to != false) ? settings.to : parseInt(obj.attr('data-percent'));
            if (to > 100) {
                to = 100;
            };
            var from = settings.from,
                loops = Math.ceil(settings.speed / settings.interval),
                increment = (to - from) / loops,
                loopCount = 0,
                interval = setInterval(updateValue, settings.interval);

            obj.find(settings.classes.skillBarBar).animate({
                width: parseInt(obj.attr('data-percent')) + '%'
            }, settings.speed);

            function updateValue() {
                from += increment;
                loopCount++;
                $(obj).find(settings.classes.skillBarPercent).text(from.toFixed(settings.decimals) + '%');

                if (typeof (settings.onUpdate) == 'function') {
                    settings.onUpdate.call(obj, from);
                }

                if (loopCount >= loops) {
                    clearInterval(interval);
                    from = to;

                    if (typeof (settings.onComplete) == 'function') {
                        settings.onComplete.call(obj, from);
                    }
                }
            }

        });
    };


   
    

    $(window).on('elementor/frontend/init', function () {

           
        elementorFrontend.hooks.addAction('frontend/element_ready/global', function ($scope) {
            AOS.init({
                duration: 500,
                easing: 'ease-out-quart',
                once: true
            });
            if ($('.react-parallax-image').length) {
                gsap.to(".react-parallax-image", {
                    scrollTrigger: {
                        // trigger: ".images",
                        start: "top bottom",
                        end: "bottom top",
                        scrub: 1,
                        // markers: true
                    },
                    x: -250,
                });
            }

            if ($('.react-parallax-image2').length) {
                gsap.to(".react-parallax-image2", {
                    scrollTrigger: {
                        // trigger: ".images",
                        start: "top bottom",
                        end: "bottom top",
                        scrub: 1,
                        // markers: true
                    },
                    y: -250,
                });
            }



        });
    });



    /* Tilter Activation */
    if ($('[data-tilt]').length) {

        $('[data-tilt]').tilt({
            perspective: 2000,
        });
    }

    // Cart show & hide
    $(document).on('click', '.menu-cart-area', function () {
        $(".cart-icon-total-products").addClass("visible-cart");
        $(".body-overlay-cart").addClass("overlayshow");
    });
    $(document).on('click', '.body-overlay-cart', function () {
        $(this).removeClass("overlayshow");
        $(".cart-icon-total-products").removeClass("visible-cart");
    });

    $(document).on('click', '.close-cart', function () {
        $(".cart-icon-total-products").removeClass("visible-cart");
        $(".body-overlay-cart").removeClass("overlayshow");
    });





})(jQuery);





