const sidebar_resize = () => {
    const navbars_h = $("body>nav").map((e, i)=>{
        return i.offsetHeight;
    }).toArray().reduce((a,b)=> a+b, 0);

    const windows_h = $(window).height();
    const sidebar = $(".sidebar");
    const siblings_h = sidebar.siblings().map((e, i)=>{return i.offsetHeight;}).toArray();
    const sibling_h = Math.max(...siblings_h);
    const sidebar_h = windows_h-navbars_h;

    $(".sidebar").outerHeight(sidebar_h > sibling_h ? sidebar_h : sibling_h);
}

function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}

function convertRange( value, r1, r2 ) { 
    return ( value - r1[ 0 ] ) * ( r2[ 1 ] - r2[ 0 ] ) / ( r1[ 1 ] - r1[ 0 ] ) + r2[ 0 ];
}
 
const toast = (message, category) => {

    let title;
        switch (category) {
            case 'success':
                title = 'Success';
                break;
            case 'warning':
                title = 'Warning';
                break;
            case 'danger':
                title = 'Error';
                break;
            default:
                title = 'Info';
        }
    
    let t = $(`<div class="toast ${category}" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header bg-primary bg-${category} bg-opacity-50">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    </div>`);

    $(".toast-container").append(t);

    show_toast(t[0]);
};

const show_toast = (el) => {
    let toast_option = {
        animation: true,
        autohide: true,
        delay: 3000
    };

    if (el.classList.contains("danger")) {
        toast_option.autohide = false;
    }

    new bootstrap.Toast(el, toast_option).show();
};

const socket = io();

$(()=>{
    $(".toast").each((i, el) => {
        show_toast(el);
    });
    
    $("a").click(function(){
        const loading_msg = $(this).attr("loading-msg");
        $("#loading_message").html(loading_msg == undefined ? "" : loading_msg);
        $("body").addClass("on_loading");
    });
});