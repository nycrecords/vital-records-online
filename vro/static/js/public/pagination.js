"use strict";

$(document).ready(function () {
    $(".page-btn").click(function (e) {
        e.preventDefault();
        $("#page").val($(this).text().trim());
        $("#browse-all-form").submit();
    });
});