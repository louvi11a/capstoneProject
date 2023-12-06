const originalValues = {}; // Store original values

    const editButton = document.getElementById("editButton");
    const saveButton = document.getElementById("saveButton");
    const cancelButton = document.getElementById("cancelButton");
    const firstNameInput = document.getElementById("firstName");
    const middleNameInput = document.getElementById("middleName");
    const lastNameInput = document.getElementById("lastName");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    // Store original values
    originalValues.firstName = firstNameInput.value;
    originalValues.middleName = middleNameInput.value;
    originalValues.lastName = lastNameInput.value;
    originalValues.username = usernameInput.value;
    originalValues.password = passwordInput.value;

    editButton.addEventListener("click", function() {
      enableInputs();
      editButton.style.display = "none";
      saveButton.style.display = "block";
      cancelButton.style.display = "block";
    });

    saveButton.addEventListener("click", function() {
      disableInputs();
      editButton.style.display = "block";
      saveButton.style.display = "none";
      cancelButton.style.display = "none";
    });

    cancelButton.addEventListener("click", function() {
      resetForm();
      disableInputs();
      editButton.style.display = "block";
      saveButton.style.display = "none";
      cancelButton.style.display = "none";
    });

    function enableInputs() {
      firstNameInput.removeAttribute("readonly");
      middleNameInput.removeAttribute("readonly");
      lastNameInput.removeAttribute("readonly");
      usernameInput.removeAttribute("readonly");
      passwordInput.removeAttribute("readonly");
    }

    function disableInputs() {
      firstNameInput.setAttribute("readonly", true);
      middleNameInput.setAttribute("readonly", true);
      lastNameInput.setAttribute("readonly", true);
      usernameInput.setAttribute("readonly", true);
      passwordInput.setAttribute("readonly", true);
    }

    function resetForm() {
      firstNameInput.value = originalValues.firstName;
      middleNameInput.value = originalValues.middleName;
      lastNameInput.value = originalValues.lastName;
      usernameInput.value = originalValues.username;
      passwordInput.value = originalValues.password;
    }