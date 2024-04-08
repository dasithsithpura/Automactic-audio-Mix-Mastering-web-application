// This JavaScript code is to make the navigation bar sticky.
window.onscroll = function() {
    var header = document.querySelector(".header");
    var sticky = header.offsetTop;
    
    if (window.pageYOffset >= sticky) {
    header.classList.add("sticky");
    } else {
    header.classList.remove("sticky");
    }
    };
    