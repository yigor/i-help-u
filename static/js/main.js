Object.keys = Object.keys || function(o) {
    var result = [];
    for(var name in o) {
        if (o.hasOwnProperty(name))
            result.push(name);
    }
    return result;
};

$(function() {
    $(document).on("click", ".login", function() {
        showAjaxDialog(this.href);
        return false;
    });

    $(document).on("click", ".register", function() {
        showAjaxDialog(this.href);
        return false;
    });

    $(document).on("click", ".password-reset", function() {
        showAjaxDialog(this.href);
        return false;
    });

    $(document).on("click", ".password-change", function() {
        showAjaxDialog(this.href);
        return false;
    });

    $(document).on("click", ".photo-change", function() {
        showAjaxDialog(this.href);
        return false;
    });

    $(document).on("click", ".dialog-close", function(){
        $("#dialog-modal").dialog("close");
    });

    $(document).on("click", "#ajax-submit", function() {
        var url = $("#ajax-form").attr("action");
        $.ajax({
            type: "POST",
            url: url,
            data: $("#ajax-form").serialize(), // serializes the form's elements.
            success: function(data)
            {
                if (data['status']) {
                    window.location = data['redirect'];
                } else {
                    $("#dialog-modal").empty().append(data['template']);
                }
            }
        });
        return false;
    });

    $(document).on("click", ".show-more-recommended", function() {
        var clicked = this;
        $.ajax({
            type: "GET",
            url: clicked.href,
            success: function(data){
                $("#update-block").empty().append(data['template']);
                $(clicked).remove();
            }
        });
        return false;
    });

    $(document).on("click", ".ui-widget-overlay", function() {
        //Close the dialog
        $("#dialog-modal").dialog("close");
    });

    $(document).on("submit", ".comments-inner form", function() {
        if (!$(this).find("textarea").val()) {
            $(this).find(".errorlist").text("Введите текст комментария");
            return false;
        }
    });

    $(document).on("click", ".reply", function() {
        // remove all reply forms
        $(".add-comment").not("#add-comment-main").remove();
        // create reply form by cloning #add-comment-main to comment div
        var addCommentDiv = $("#add-comment-main");
        var action = addCommentDiv.find("form").attr("action");
        var replyContainerDiv = $("#comment_" + $(this).data("comment"));
        replyContainerDiv.find("hr").before(addCommentDiv.clone().removeAttr("id"));
        // set parent param in reply form action
        replyContainerDiv.find("form").attr("action", action + "?parent=" + $(this).data("reply"));
        replyContainerDiv.find(".errorlist").text("");
        // show reply form
        $(".add-comment").not("#add-comment-main").children().not("a").show();
        $(".add-comment").not("#add-comment-main").children("a").hide();
        // hide add comment form
        addCommentDiv.children().not("a").hide();
        addCommentDiv.children("a").show();
        return false;
    });

    $(document).on("click", ".show-comment-form", function() {
        // remove all reply forms
        $(".add-comment").not("#add-comment-main").remove();
        // show add comment form
        var addCommentDiv = $("#add-comment-main");
        addCommentDiv.children().not("a").show();
        addCommentDiv.children("a").hide();
        return false;
    });

    $(document).on("click", "#comment-scroll", function() {
        setTimeout(function() {$("#add-comment-main").find("textarea").focus()}, 100);
    });

    $(document).on("click", ".filter li a:not(.clear-filter)", function(e) {
        var uri = new URI(document.location.search);
        var newUri = new URI($(this).attr("href"));

        if ($(this).parent().hasClass("active")) {
            uri.removeSearch(newUri.search(true));
        } else {
            uri.addSearch(newUri.search(true));
        }

        applyFilter(uri, e);
        return false;
    });

    $(document).on("click", ".toggle-filter li a", function(e) {
        var uri = new URI(document.location.search);
        var newUri = new URI($(this).attr("href"));

        uri.removeSearch(Object.keys(newUri.search(true)));
        if (!$(this).parent().hasClass("active")) {
            uri.addSearch(newUri.search(true));
        }

        applyFilter(uri, e);
        return false;
    });

//    $(document).on("submit", ".list-search", function(e) {
//        if (Modernizr.history) {
//            var uri = new URI(document.location.search);
//            uri.setSearch({'q': $(this).find("input[name=q]").val()});
//            applyFilter(uri, e);
//        }
//    });
});

//var popped = ('state' in window.history && window.history.state !== null), initialURL = location.href;

//window.onpopstate = function(e) {
////    var initialPop = !popped && location.href == initialURL;
////    popped = true;
////    if ( initialPop ) return;
//    var uri = new URI(document.location);
//    if (!$.inArray(uri.path(), ["/organization/", "/vacancy/"])) return;
//    var state = e.state;
//
//    if (!state) {
//        state = uri.search(true);
//    }
//
//
//    uri.search(state);
//    var url = uri.search().toString() ? uri.search().toString() : "?";
//    $.ajax({
//        type: "GET",
//        url: url,
//        success: function(data){
//            $("#update-block").empty().append(data['template']);
//        }
//    });
//    markFiltersActive(state);
//};

function applyFilter(uri, e) {
    document.location.search = uri;
//    if (Modernizr.history) {
//        var url = uri.toString() ? uri.toString() : "?";
//        history.pushState(uri.search(true), null, url);
//        e.preventDefault();
//        markFiltersActive(uri.search(true));
//        $.ajax({
//            type: "GET",
//            url: url,
//            success: function(data){
//                $("#update-block").empty().append(data['template']);
//            }
//        });
//    } else {
//        document.location.search = uri;
//    }
}

function markFiltersActive(currentFilter) {
    var q = currentFilter ? currentFilter.q : "";
    $(".list-search").find("input[name=q]").val(q);
    delete currentFilter.q;

    if (currentFilter && !$.isEmptyObject(currentFilter)) {
        $(".filter li a:not(.clear-filter), .toggle-filter li a").each(function() {
            var filter = new URI($(this).attr("href")).search(true);
            for (var key in filter) {
                if ($.inArray(filter[key], currentFilter[key]) > -1) {
                    $(this).parent().addClass("active");
                } else {
                    $(this).parent().removeClass("active");
                }
            }
        });
        $(".clear-filter").parent().removeClass("active");
    } else {
        $(".filter li a:not(.clear-filter), .toggle-filter li a").parent().removeClass("active");
        $(".clear-filter").parent().addClass("active");
    }
}

function showAjaxDialog(url, redirectOnClose) {
    $.ajax({
        type: "GET",
        url: url,
        success: function(data){
            var template = data['template'] ? data['template'] : data;
            $("#dialog-modal").append(template);
            uLogin.customInit($(".uLogin").attr("id"));
        }

    });
    var dialogModal = $("#dialog-modal");
    dialogModal.empty();
    dialogModal.dialog({
        dialogClass: "no-close",
        position: { my: "top-300", at: "center", of: window },
        width: 380,
        height: 630,
        modal: true,
        beforeClose: function(event, ui) {
            $("body").css({ overflow: 'inherit' });
        },
        open: function(event, ui) {
            $("body").css({ overflow: 'hidden' });
        },
        close: function(event, ui) {if (redirectOnClose) {window.location = '/'}}
    });
}

function loadMore(button) {
    var clicked = button;
    var link_postfix =  $(button).data('link_postfix');
    var url = $(button).data('load-url') + '?page=' + $(button).data('next-page') + (link_postfix ? '&' + link_postfix : '');
    $(".last-line").css("visibility", "");
    $.ajax({
        type: "GET",
        url: url,
        success: function(data){
            $("#update-block").append(data['template']);
            $(clicked).remove();
        }
    });
}
