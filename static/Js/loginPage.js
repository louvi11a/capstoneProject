function togglePasswordVisibility(id, event) {
    var passwordField = document.getElementById(id);
    var passwordToggle = event.target;
    if (passwordField.type === "password") {
        passwordField.type = "text";
        passwordToggle.classList.remove('bi-eye-fill');
        passwordToggle.classList.add('bi-eye-slash-fill');
    } else {
        passwordField.type = "password";
        passwordToggle.classList.remove('bi-eye-slash-fill');
        passwordToggle.classList.add('bi-eye-fill');
    }
}