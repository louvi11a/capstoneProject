const uploadForm = document.getElementById("uploadFileForm");
const fileInput = document.getElementById("file");
const uploadProgress = document.getElementById("uploadProgress");
const uploadMessage = document.getElementById("uploadMessage");
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}



$(document).ready(function() {
// When the Details link is clicked...
$('.dropdown-item').on('click', function() {
  // Get the file ID from the data-file-id attribute
  var fileID = $(this).data('file-id');

  // Send an AJAX request to the file_details view
  $.ajax({
      url: '/orphans/files/details/' + fileID + '/',  // Update with your actual URL
      type: 'GET',
      success: function(data) {
          // Update the modal with the returned data
          $('#modalFileName').text(data.fileName);
          $('#modalFileType').text(data.fileType);
          $('#modalFileSize').text(data.fileSize);
          $('#modalDateUploaded').text(data.dateUploaded);
      }
  });
});
});

// uploading file
document.addEventListener('DOMContentLoaded', function() {
  const uploadForm = document.getElementById("uploadFileForm");
  const fileInput = document.getElementById("file");
  const uploadProgress = document.getElementById("uploadProgress");
  const uploadMessage = document.getElementById("uploadMessage");

  if (uploadForm) {
      uploadForm.addEventListener("submit", function(event) {
          event.preventDefault();

          // Validate file selection
          if (!fileInput.files.length) {
              uploadMessage.textContent = "Please select a file to upload.";
              return;
          }

          // Show upload progress indicator
          uploadProgress.style.display = "block";

          // Create a FormData object and append the file
          var formData = new FormData(uploadForm);

          // Send a POST request to the server
          fetch("/orphans/upload_file/", {
              method: "POST",
              body: formData,
          })
          .then((response) => {
              if (!response.ok) {
                  throw new Error("Network response was not ok: " + response.statusText);
              }
              return response.json();
          })
          .then((data) => {
              uploadProgress.style.display = "none";
              if (data.message) {
                  uploadMessage.textContent = data.message;
              }
          })
          .catch((error) => {
              uploadProgress.style.display = "none";
              uploadMessage.textContent = "Upload failed: " + error.message;
              console.error("Error:", error);
          });
      });
  } else {
      console.log('Upload form not found');
  }
});


function handleRename() {
  const csrfToken = getCookie("csrftoken"); // Get the CSRF token from the cookies
  const fileId = document.getElementById("renameFileId").value;
  const newFileName = document.getElementById("newFileNameInput").value;

  fetch("/orphans/rename_file/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken, // Include the CSRF token in the request header
    },
    body: JSON.stringify({ fileId: fileId, newFileName: newFileName }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      // Handle success
    })
    .catch((error) => {
      // Handle errors
    });
}
