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

    // Check if the first input field is readonly or disabled
    if (inputs[0].hasAttribute('readonly') || inputs[0].hasAttribute('disabled')) {
        // If the input fields are readonly or disabled, make them editable and change the button text to "Save"
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].removeAttribute('readonly');
            inputs[i].removeAttribute('disabled');
        }
        editButton.textContent = 'Save';
    } else {
        // If the input fields are editable, make them readonly or disabled and change the button text to "Edit"
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].type === "radio" || inputs[i].type === "checkbox") {
                inputs[i].setAttribute('disabled', true);
            } else {
                inputs[i].setAttribute('readonly', true);
            }
        }
        editButton.textContent = 'Edit';

        // Call a function to save the changes
        saveChanges(sectionId, orphanId);
    }
}

function collectData(sectionId) {
    var data = {};

    // Collect data based on the section being edited
    switch (sectionId) {
        case 'personal-info':
            // Collect personal info fields
            data['firstName'] = document.getElementById('firstName').value;
            data['middleName'] = document.getElementById('middleName').value;
            data['lastName'] = document.getElementById('lastName').value;
            data['gender'] = document.getElementById('gender').value;
            data['birthDate'] = document.getElementById('birthDate').value;
            data['dateAdmitted'] = document.getElementById('dateAdmitted').value;
            break;
        case 'family-info':
            // Collect family info fields
            data['mothersName'] = document.getElementById('mothersName').value;
            data['fathersName'] = document.getElementById('fathersName').value;
            data['homeAddress'] = document.getElementById('homeAddress').value;
            break;
        case 'educational-background':
            // Collect educational background fields
            data['quarter'] = document.getElementById('quarter').value;
            data['school_year'] = document.getElementById('school_year').value;
            data['education_level'] = document.getElementById('education_level').value;
            data['school_name'] = document.getElementById('school_name').value;
            data['current_gpa'] = document.getElementById('current_gpa').value;
            break;
        case 'physical-health':
            // Collect physical health fields
            data['height'] = document.getElementById('height').value;
            data['weight'] = document.getElementById('weight').value;
            break;
        // Add more cases as needed for other sections
    }

    return data;
}


function saveChanges(sectionId, orphanId) {
    // Call collectData to get the form data for the specific section
    var data = collectData(sectionId); // Pass sectionId to collectData

    // Check if birthDate and dateAdmitted are in the correct format
    var datePattern = /^\d{4}-\d{2}-\d{2}$/; // YYYY-MM-DD format
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
    console.log('globalOrphanId:', orphanId);
    xhr.open('POST', '/orphans/save_changes/' + orphanId + '/', true);
    xhr.setRequestHeader('Content-Type', 'application/json'); // Set the Content-Type header to 'application/json'
    xhr.setRequestHeader('X-CSRFToken', csrftoken);

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) { // The request is complete
            if (xhr.status == 200) { // The request was successful
                console.log('Changes saved successfully');
                // You may want to reload the page or update the UI to reflect the changes
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

document.addEventListener('DOMContentLoaded', function() {
    // Function to calculate BMI
    function calculateBMI(height, weight) {
        if (height > 0 && weight > 0) {
            let heightInMeters = height / 100; // Convert height from cm to meters
            return weight / (heightInMeters ** 2); // BMI formula
        }
        return null;
    }

    // Function to determine BMI category
    function getBMICategory(bmi) {
        if (bmi < 18.5) {
            return 'Underweight';
        } else if (bmi >= 18.5 && bmi < 25) {
            return 'Normal weight';
        } else if (bmi >= 25 && bmi < 30) {
            return 'Overweight';
        } else if (bmi >= 30) {
            return 'Obesity';
        }
        return '';
    }

    // Function to update BMI category on the page
    function updateBMICategory() {
        var height = parseFloat(document.getElementById('height').value);
        var weight = parseFloat(document.getElementById('weight').value);
        var bmi = calculateBMI(height, weight);
        var bmiCategory = getBMICategory(bmi);
        document.getElementById('bmi_category').value = bmiCategory;
    }

    // Add event listeners to the height and weight input fields
    var heightElement = document.getElementById('height');
    var weightElement = document.getElementById('weight');

    if (heightElement && weightElement) {
        heightElement.addEventListener('input', updateBMICategory);
        weightElement.addEventListener('input', updateBMICategory);
    } else {
        console.error('Height or weight element not found');
    }
});
