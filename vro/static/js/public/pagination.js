"use strict";

$(document).ready(function () {
    $(".page-btn").click(function (e) {
        e.preventDefault();
        let current_page = $(".btn-dark").text().trim();
        if ($(this).text().trim() === "»") {
            $("#page").val(parseInt(current_page) + 1);
        }
        else if ($(this).text().trim() === "«") {
            $("#page").val(parseInt(current_page) - 1);
        }
        else {
            $("#page").val($(this).text().trim());
        }
        $("#browse-all-form").submit();
    });




    $("#previous").click(function (e) {
        e.preventDefault();
        $("#page").val("previous");
        $("#browse-all-form").submit();
    });

    $("#next").click(function (e) {
        e.preventDefault();
        $("#page").val("next");
        $("#browse-all-form").submit();
    });

    $("#last").click(function (e) {
        e.preventDefault();
        $("#page").val("last");
        $("#browse-all-form").submit();
    });

    $("#first").click(function (e) {
        e.preventDefault();
        $("#page").val("first");
        $("#browse-all-form").submit();
    });
});