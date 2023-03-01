// requires a div with id="dismiss-container"
function dismissableError(errorMessage)
{
    document.getElementById("dismiss-container").innerHTML = `<div div class="alert alert-warning alert-dismissible" role="alert">\
    ${errorMessage}\
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">x</button>\
</div>\
`;

window.focus();
}