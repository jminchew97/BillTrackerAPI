document.write('<nav class="navbar navbar-expand-lg navbar-dark bg-dark">\
  <a class="navbar-brand" href="#">Billy</a>\
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">\
    <span class="navbar-toggler-icon"></span>\
  </button>\
  <div class="collapse navbar-collapse" id="navbarNavAltMarkup">\
    <div class="navbar-nav">\
      <a class="nav-item nav-link" href="http://127.0.0.1:5000/">Home <span class="sr-only">(current)</span></a>\
      <a class="nav-item nav-link" id="dashboardButton-nav" href="http://127.0.0.1:5000/dashboard">Dashboard</a>\
      <a class="nav-item nav-link" id="loginButton-nav" href="http://127.0.0.1:5000/login">Login</a>\
      <a class="nav-item nav-link" id="signupButton-nav" href="http://127.0.0.1:5000/signup">Signup</a>\
      <a class="nav-item nav-link" id="logoutButton-nav" href="http://127.0.0.1:5000/">Logout</a>\
    </div>\
  </div>\
</nav>\
');


//write code to manage buttons if logged in or logged out
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
// user is not logged in
if (getCookie("csrf_access_token") == "")
{
  document.getElementById("dashboardButton-nav").style.display = "none";
  document.getElementById("logoutButton-nav").style.display = "none";
}
else
{
  let displayStyle = "block"
  document.getElementById("dashboardButton-nav").style.display = displayStyle;
  document.getElementById("logoutButton-nav").style.display = displayStyle;

  document.getElementById("signupButton-nav").style.display ="none";
  document.getElementById("loginButton-nav").style.display ="none";
}
// logout functionality to logout button
document.getElementById("logoutButton-nav").addEventListener("click",logUserOut, false);

  function logUserOut(event){
    event.preventDefault();

    fetch('http://127.0.0.1:5000/logout_with_cookies', {
        method: 'POST',
        headers: {
            accept: 'application.json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jdata),
        cache: 'default'
    }).then(resp =>
    {
      if (resp.ok)
      {
        return resp.json().then(jdata=> console.log(jdata)).then(() => {window.location.assign('http://127.0.0.1:5000/login')})
      }
      else 
      {
        return resp.json().then((jdata)=> {
          alert(jdata["message"]);
        });
      }
    })
}
