"use strict";

$(document).ready(function () {
    $("#search-by-name-form").hide();
    $("#form-type-select").change(function () {
        if(this.value === "number") {
            $("#search-by-number-form").show();
            $("#search-by-name-form").hide();
        }
        else {
            $("#search-by-number-form").hide();
            $('#search-by-name-form').removeAttr("hidden");
            $("#search-by-name-form").show();
        }
    });
});