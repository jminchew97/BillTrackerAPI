// requires a div with id="dismiss-container"
function dismissableError(errorMessage)
{
    document.getElementById("dismiss-container").innerHTML = `<div class="alert alert-danger alert-dismissible fade show" role="alert">\
    ${errorMessage}\
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>\
</div>\
`;

window.focus();
}