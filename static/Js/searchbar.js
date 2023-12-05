$('#search-bar').on('input', function() {
    $.ajax({
        url: '/search_suggestions/',
        data: {
            'q': $(this).val()
        },
        dataType: 'json',
        success: function(data) {
            // Here you should update your search suggestions dropdown with the data.
        }
    });
});

$('#search-suggestions-dropdown').on('click', 'a', function() {
    window.location.href = $(this).data('url');
});