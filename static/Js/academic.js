document.addEventListener('DOMContentLoaded', function() {
    var educationLevelInput = document.getElementById('educationLevelInput');
    var educationOptions = [
        { value: 'Elementary', text: 'Elementary' },
        { value: 'High School', text: 'High School' },
        { value: 'College', text: 'College' }
    ];
        // Add options to educationLevelInput
        for (var i = 0; i < educationOptions.length; i++) {
            var option = document.createElement('option');
            option.value = educationOptions[i].value;
            option.text = educationOptions[i].text;
            educationLevelInput.appendChild(option);
        }
    educationLevelInput.value = 'Elementary';  // Set default value

    var quarterInput = document.getElementById('quarterInput');
    var yearLevelInput = document.getElementById('yearLevelInput');

    function populateDropdowns() {
        // Remove existing options
        while (quarterInput.firstChild) {
            quarterInput.removeChild(quarterInput.firstChild);
        }
        yearLevelInput.innerHTML = '';

        var quarterOptions;
        var yearOptions;
        if (educationLevelInput.value === 'College') {
            quarterOptions = [
                {value: '1', text: 'First Semester'},
                {value: '2', text: 'Second Semester'}
            ];
            yearOptions = [
                { value: 1, text: 'First Year' },
                { value: 2, text: 'Second Year' },
                { value: 3, text: 'Third Year' },
                { value: 4, text: 'Fourth Year' }
            ];
        } else if (educationLevelInput.value === 'High School') {
            quarterOptions = [
                {value: '1', text: 'First Quarter'},
                {value: '2', text: 'Second Quarter'},
                {value: '3', text: 'Third Quarter'},
                {value: '4', text: 'Fourth Quarter'}
            ];
            yearOptions = [
                { value: 7, text: 'Grade 7' },
                { value: 8, text: 'Grade 8' },
                { value: 9, text: 'Grade 9' },
                { value: 10, text: 'Grade 10' },
                { value: 11, text: 'Grade 11' },
                { value: 12, text: 'Grade 12' }

            ];
        } else { // Elementary
            quarterOptions = [
                {value: '1', text: 'First Quarter'},
                {value: '2', text: 'Second Quarter'},
                {value: '3', text: 'Third Quarter'},
                {value: '4', text: 'Fourth Quarter'}
            ];
            yearOptions = [
                { value: 1, text: 'Grade 1' },
                { value: 2, text: 'Grade 2' },
                { value: 3, text: 'Grade 3' },
                { value: 4, text: 'Grade 4' },
                { value: 5, text: 'Grade 5' },
                { value: 6, text: 'Grade 6' }
            ];
        }

        // Add new options to quarterInput
        for (var i = 0; i < quarterOptions.length; i++) {
            var option = document.createElement('option');
            option.value = quarterOptions[i].value;
            option.text = quarterOptions[i].text;
            quarterInput.appendChild(option);
        }

        // Add new options to yearLevelInput
        for (var i = 0; i < yearOptions.length; i++) {
            var option = document.createElement('option');
            option.value = yearOptions[i].value;
            option.text = yearOptions[i].text;
            yearLevelInput.appendChild(option);
        }
    }

    // Populate dropdowns when the page is loaded
    populateDropdowns();

    // Populate dropdowns when the 'educationLevelInput' dropdown changes
    educationLevelInput.addEventListener('change', populateDropdowns);

    
});