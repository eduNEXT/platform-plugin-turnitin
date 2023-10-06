/* Javascript for TurnitinXBlock. */
function TurnitinXBlock(runtime, element) {

  function updateCount(result) {
      $('.count', element).text(result.count);
  }

  function showEULA(htmlContent) {
      $('#eulaModal .modal-content p').html(htmlContent);
      $('#eulaModal').show();
  }

  function closeModal() {
      $('#eulaModal', element).hide();
  }

  var handlerUrl = runtime.handlerUrl(element, 'increment_count');

  $('p', element).click(function(eventObject) {
      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),
          success: updateCount
      });
  });

  $('#viewEULA', element).click(function() {
      var handlerUrl = runtime.handlerUrl(element, 'get_eula_agreement');

      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),

          success: function(response) {
            if(response.status >= 400) {
                alert(`ERROR: ${response.status} - No EULA page for the given version was found`);
            } else {
                showEULA(response.html);
            }
          },
          error: function() {
              alert('Error getting EULA.');
          }
      });
  });

  $('#acceptEULA', element).click(function() {
      var handlerUrl = runtime.handlerUrl(element, 'accept_eula_agreement');

      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),
          success: function(response) {
            if(response.success === false && response.status >= 400) {
                alert(`ERROR: ${response.status} - ${response.message}`);
            } else {
                alert('EULA successfully accepted!');
            }
          },
          error: function() {
              alert('Error accepting EULA.');
          }
      });
  });

  $('.modal-content button').click(closeModal);

  $('#uploadBtn', element).click(function(event) {
      event.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'upload_turnitin_submission_file');

      var fileInput = $('#file')[0];
      var file = fileInput.files[0];

      if (!file) {
          alert('Please select .doc or .docx files.');
          return;
      }

      var formData = new FormData();
      formData.append('myfile', file);

      $.ajax({
          type: 'POST',
          url: handlerUrl,
          data: formData,
          processData: false,
          contentType: false,
          success: function(response) {
            if(response.success === false && response.status >= 400) {
                alert(`ERROR: ${response.status} - ${response.message}`);
            } else {
                alert('File successfully uploaded to Turnitin!');
            }
          },
          error: function() {
              alert('Error uploading file.');
          }
      });
  });

  function updateSelectedFileName() {
      var fileName = $(this).val().split('\\').pop();
      var fileExtension = fileName.split('.').pop().toLowerCase();
      var uploadButton = $('#uploadBtn');

      if (fileExtension === 'doc' || fileExtension === 'docx') {
          if (fileName) {
              $(this).siblings('.selected-filename').text(fileName);
              $(this).siblings('label').addClass('file-selected').text('Change File');
              uploadButton.prop('disabled', false);
          } else {
              $(this).siblings('.selected-filename').text('No file selected');
              $(this).siblings('label').removeClass('file-selected').text('Choose File');
              uploadButton.prop('disabled', true);
          }
      } else {
          alert('Please, select .doc or .docx files');
          $(this).val('');
          $(this).siblings('.selected-filename').text('No file selected');
          $(this).siblings('label').removeClass('file-selected').text('Choose File');
          uploadButton.prop('disabled', true);
      }
  }
  $('#file', element).on('change', updateSelectedFileName);

  $('#refreshBtn1', element).click(function(event) {
      event.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'get_submission_status');

      $.ajax({
        type: "POST",
        url: handlerUrl,
        data: JSON.stringify({"hello": "world"}),
        success: function(response) {
          if(response.success === false && response.status >= 400) {
              updateTrafficLightState('1', 'ERROR');
              alert(`ERROR: ${response.status} - ${response.message}`);
          } else {
              updateTrafficLightState('1', response['status']);
          }
        },
        error: function() {
            alert('Error getting report status.');
        }
    });
  });


  $('#generateReportBtn1', element).click(function(event) {
      event.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'generate_similarity_report');

      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),
          success: function(response) {
            if(response.success === false && response.status >= 400) {
                alert(`ERROR: ${response.status} - ${response.message}`);
            } else {
                alert('Successfully scheduled similarity report generation.');
            }
          },
          error: function() {
              alert('Error in similarity report generation.');
          }
      });
  });




  $('#refreshBtn2', element).click(function(event) {
      event.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'get_similarity_report_status');

      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),
          success: function(response) {
            if(response.success === false && response.status >= 400) {
                updateTrafficLightState('2', 'ERROR');
                alert(`ERROR: ${response.status} - ${response.message}`);
            } else {
                updateTrafficLightState('2', response['status']);
            }
          },
          error: function() {
              alert('Error getting report status.');
          }
      });
  });


  $('#generateReportBtn2', element).click(function(event) {
      event.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'create_similarity_viewer');

      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),
          success: function(response) {
              if(response.success === false && response.status >= 400) {
                alert(`ERROR: ${response.status} - ${response.message}`);
            } else {
                alert('Redirecting...');
                openInNewTab(response.viewer_url);
            }
          },
          error: function() {
              alert('Error getting Viewer URL.');
          }
      });
  });


  function openInNewTab(url) {
      window.open(url, '_blank');
  }


  function updateTrafficLightState(semaphoreNumber, state) {
      console.log(state);
      const redLight = document.getElementById(`redLight${semaphoreNumber}`);
      const yellowLight = document.getElementById(`yellowLight${semaphoreNumber}`);
      const greenLight = document.getElementById(`greenLight${semaphoreNumber}`);
      const generateReportBtn = document.getElementById(`generateReportBtn${semaphoreNumber}`);
      const statusText = document.getElementById(`statusText${semaphoreNumber}`);
      const refreshBtn2 = document.getElementById(`refreshBtn2`);

      redLight.classList.add('off');
      yellowLight.classList.add('off');
      greenLight.classList.add('off');
      generateReportBtn.disabled = true;
      generateReportBtn.classList.remove('enabled');
      statusText.textContent = state;

      statusText.classList.remove('red-text', 'yellow-text', 'green-text');

      switch (state) {
          case 'ERROR':
              redLight.classList.remove('off');
              statusText.classList.add('red-text');
              break;
          case 'PROCESSING':
              yellowLight.classList.remove('off');
              statusText.classList.add('yellow-text');
              break;
          case 'COMPLETE':
              greenLight.classList.remove('off');
              statusText.classList.add('green-text');
              generateReportBtn.disabled = false;
              generateReportBtn.classList.add('enabled');
              refreshBtn2.disabled = false;
              refreshBtn2.classList.add('enabled');
              break;
        default:
            redLight.classList.remove('off');
            statusText.classList.add('red-text');
      }
  }

}
