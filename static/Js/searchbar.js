console.log('searchbar.js is loaded');  // Debugging line

$(document).ready(function() {
    console.log('Document is ready');  // Debugging line
    $('#searchBox').on('input', function() {
        console.log('Input event fired');  // Debugging line
        $.ajax({
            url: '/search_suggestions/',
            data: {
                'q': $(this).val()
            },
            dataType: 'json',
            success: function(data) {
                console.log('AJAX request succeeded');  // Debugging line
                // rest of the code...
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('AJAX request failed');  // Debugging line
                console.log('jqXHR:', jqXHR);
                console.log('textStatus:', textStatus);
                console.log('errorThrown:', errorThrown);
            }
        });
    });
});