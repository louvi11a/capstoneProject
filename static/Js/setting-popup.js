function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          let cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}




console.log("Script loaded");

const originalValues = {}; // Store original values

const editButton = document.getElementById("editButton");
const saveButton = document.getElementById("saveButton");
const cancelButton = document.getElementById("cancelButton");
const firstNameInput = document.getElementById("firstName");
const emailInput = document.getElementById("email");
const lastNameInput = document.getElementById("lastName");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");

// Store original values
originalValues.firstName = firstNameInput.value;
originalValues.email = emailInput.value; 
originalValues.lastName = lastNameInput.value;
originalValues.username = usernameInput.value;
originalValues.password = passwordInput.value;

editButton.addEventListener("click", function() {
  console.log("Edit button clicked");
  enableInputs();
  editButton.style.display = "none";
  saveButton.style.display = "block";
  cancelButton.style.display = "block";
});

saveButton.addEventListener("click", function() {
  console.log("Save button clicked");
  disableInputs();
  editButton.style.display = "block";
  saveButton.style.display = "none";
  cancelButton.style.display = "none";

  // Send a POST request to the server with the updated information
  console.log(getCookie('csrftoken'));

  $.ajax({
    url: '/users/update_user_info/',  // Replace with the correct URL
    type: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    },
    data: {
        'username': usernameInput.value,
        'firstName': firstNameInput.value,
        'lastName': lastNameInput.value,
        'email': emailInput.value,
        'password': passwordInput.value,
        // Include any other data you want to send to the server
    },
    success: function(response) {
      console.log("AJAX request successful", response);
        // The request was successful, you can update the UI here if you want
    },
    error: function(response) {
      console.log("AJAX request failed", response);
      alert("Failed to update. Please try again later.");
    

        // There was an error, handle it here
    }
  });
});

cancelButton.addEventListener("click", function() {
  console.log("Cancel button clicked");
  resetForm();
  disableInputs();
  editButton.style.display = "block";
  saveButton.style.display = "none";
  cancelButton.style.display = "none";
});

function enableInputs() {
  usernameInput.removeAttribute("readonly");
  firstNameInput.removeAttribute("readonly");
  lastNameInput.removeAttribute("readonly");
  emailInput.removeAttribute("readonly");
  passwordInput.removeAttribute("readonly");
}

function disableInputs() {
  usernameInput.setAttribute("readonly", true);
  firstNameInput.setAttribute("readonly", true);
  lastNameInput.setAttribute("readonly", true);
  emailInput.setAttribute("readonly", true);
  passwordInput.setAttribute("readonly", true);
}

function resetForm() {
  usernameInput.value = originalValues.username;
  firstNameInput.value = originalValues.firstName;
  lastNameInput.value = originalValues.lastName;
  emailInput.value = originalValues.email;
  passwordInput.value = originalValues.password;
}

function submitChangePasswordForm() {
  const form = document.getElementById('changePasswordForm');
  form.submit();
}

// function togglePasswordVisibility(inputId) {
//   var passwordInput = document.getElementById(inputId);
//   var passwordType = passwordInput.getAttribute('type');
//   var eyeIcon = passwordInput.nextElementSibling.children[0]; // get the eye icon

//     console.log(eyeIcon); // Add this line

//   if (passwordType == 'password') {
//       passwordInput.setAttribute('type', 'text');
//       eyeIcon.className = 'bi bi-eye-slash'; // set the class to eye-slash
//       console.log(eyeIcon.className);
//   } else {
//       passwordInput.setAttribute('type', 'password');
//       eyeIcon.className = 'bi bi-eye-fill'; // set the class to eye
//   }
//       console.log(eyeIcon.className);
// }


function togglePasswordVisibility(inputId, event) {
  event.preventDefault();
  const passwordInput = document.getElementById(inputId);
  const icon = document.querySelector(`[data-toggle-password="${inputId}"] i`);

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    icon.classList.remove('bi-eye-fill');
    icon.classList.add('bi-eye-slash-fill');
  } else {
    passwordInput.type = 'password';
    icon.classList.remove('bi-eye-slash-fill');
    icon.classList.add('bi-eye-fill');
  }
}