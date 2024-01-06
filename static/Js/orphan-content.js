console.log('orphan-content.js is loaded');
// rest of your code

var globalOrphanId;

window.onload = function() {
 globalOrphanId = getOrphanId();
};

function getOrphanId() {
    var url = window.location.pathname;
    var segments = url.split('/');
    var orphanId = segments[segments.length - 2];
    console.log('Extracted orphanId:', orphanId);
    return orphanId;
}

 function toggleEdit(sectionId, orphanId) {
    console.log('toggleEdit is called with sectionId:', sectionId);
 
    // Get the edit button and input fields in the section
    var editButton = document.getElementById('edit-' + sectionId);
    var inputs = document.getElementById(sectionId).getElementsByTagName('input');
 
    // Check if the input fields are readonly
    if (inputs[0].hasAttribute('readonly')) {
        // If the input fields are readonly, make them editable and change the button text to "Save"
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].removeAttribute('readonly');
        }
        editButton.textContent = 'Save';
    } else {
        // If the input fields are editable, make them readonly and change the button text to "Edit"
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].setAttribute('readonly', true);
        }
        editButton.textContent = 'Edit';
 
        // Call a function to save the changes
        saveChanges(sectionId, orphanId);
    }
 }

function saveChanges(sectionId, orphanId) {
    // Get the input fields in the section
    var inputs = document.getElementById(sectionId).getElementsByTagName('input');
 
    // Create an object to store the new data
    var data = {};
    for (var i = 0; i < inputs.length; i++) {
        data[inputs[i].id] = inputs[i].value;
    }

    // Check if birthDate and dateAdmitted are in the correct format
    var datePattern = /^\d{4}-\d{2}-\d{2}$/;
    if ('birthDate' in data && !datePattern.test(data['birthDate'])) {
        console.error('birthDate is not in the correct format');
        return;
    }
    if ('dateAdmitted' in data && !datePattern.test(data['dateAdmitted'])) {
        console.error('dateAdmitted is not in the correct format');
        return;
    }
    console.log('Dates are in the correct format');
 
    // Get the CSRF token from a cookie
    var csrftoken = getCookie('csrftoken');
 
    // Send a POST request to the Django view
    var xhr = new XMLHttpRequest();
    console.log('globalOrphanId:', globalOrphanId);
    xhr.open('POST', '/orphans/save_changes/' + globalOrphanId + '/', true);
    xhr.setRequestHeader('Content-Type', 'application/json');  // Set the Content-Type header to 'application/json'
    xhr.setRequestHeader('X-CSRFToken', csrftoken);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) { // The request is complete
            if (xhr.status == 200) { // The request was successful
                console.log('Changes saved successfully');
            } else {
                console.error('Failed to save changes');
            }
        }
    };

    xhr.send(JSON.stringify(data));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Get the height, weight, and bmi_category fields
var heightField = document.getElementById('height');
var weightField = document.getElementById('weight');
var bmiCategoryField = document.getElementById('bmi_category');

// Define a mapping from BMI ranges to BMI categories
var bmiCategories = {
    '< 18.5': 'Underweight',
    '18.5 - 24.9': 'Normal Weight',
    '25 - 29.9': 'Overweight',
    '30 or more': 'Obesity',
};

// Define a function to calculate the BMI category
function calculateBmiCategory() {
    var height = parseFloat(heightField.value);
    var weight = parseFloat(weightField.value);
    if (!isNaN(height) && !isNaN(weight)) {
        var heightM = height / 100;  // convert cm to m
        var bmi = weight / (heightM ** 2);
        var bmiRange;
        if (bmi < 18.5) {
            bmiRange = '< 18.5';
        } else if (bmi < 25) {
            bmiRange = '18.5 - 24.9';
        } else if (bmi < 30) {
            bmiRange = '25 - 29.9';
        } else {
            bmiRange = '30 or more';
        }
        var bmiCategory = bmiCategories[bmiRange];
        bmiCategoryField.value = bmiCategory;
    }
}

// Add event listeners to the height and weight fields to call calculateBmiCategory when their values change
heightField.addEventListener('input', calculateBmiCategory);
weightField.addEventListener('input', calculateBmiCategory);