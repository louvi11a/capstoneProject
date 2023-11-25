    // JavaScript to show/hide the dropdown content for all buttons with the class "dropdown-button"
    var buttons = document.querySelectorAll(".dropdown-button");
    
    buttons.forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.stopPropagation();
            var dropdown = button.nextElementSibling;
            if (dropdown.style.display === "block") {
                dropdown.style.display = "none";
            } else {
                dropdown.style.display = "block";
            }
        });
    });

    document.addEventListener("click", function(event) {
        buttons.forEach(function(button) {
            var dropdown = button.nextElementSibling;
            if (event.target !== button) {
                dropdown.style.display = "none";
            }
        });
    });