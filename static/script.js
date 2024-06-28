/**
 * REST Client
 *
 */

function getUsers() {
    var req = new XMLHttpRequest();
    req.open("GET", "/api/user/");
    try {
        req.setRequestHeader("Authorization", "Basic " + btoa("homer:1234"));
    } catch (e) {
        console.error("Failed to set authorization header", e);
    }
    req.addEventListener("load", function() {
        if (this.status === 200) {
            var user = JSON.parse(this.responseText);
            var ul = document.getElementById('users');
            ul.innerHTML = '';
            var li = document.createElement('li');
            li.innerHTML = `${user.name} (${user.username}) - ${user.email}`;
            ul.appendChild(li);
        } else {
            alert("Failed to load user details");
        }
    });
    req.send();
}

function registerUser(event) {
    event.preventDefault();
    var form = document.getElementById('registerForm');
    var username = form.username.value;
    var password = form.password.value;
    var name = form.name.value;
    var email = form.email.value;

    var req = new XMLHttpRequest();
    req.open("POST", "/api/user/register/");
    req.setRequestHeader("Content-Type", "application/json");
    req.addEventListener("load", function() {
        if (this.status === 201) {
            alert("User registered successfully!");
            getUsers();
        } else {
            alert("Failed to register user");
        }
    });
    req.send(JSON.stringify({"username": username, "password": password, "name": name, "email": email}));
}

document.addEventListener("DOMContentLoaded", function() {
    getUsers();
});
