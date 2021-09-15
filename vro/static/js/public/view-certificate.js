"use strict";

$(document).ready(function () {
    let url = $("#blob-url").attr("href");
    PDFObject.embed(url, "#pdf-viewer");
});