/* Javascript for TurnitinXBlock. */
function TurnitinXBlock(runtime, element) {

  function updateCount(result) {
      $('.count', element).text(result.count);
  }

  function showEULA(htmlContent) {
      $('#eulaModal .modal-content p').html(htmlContent); // Establece el contenido HTML en el párrafo del modal
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
              showEULA(response);
          },
          error: function() {
              alert('Error al obtener el contenido del EULA.');
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
              alert('EULA accepted!.');
          },
          error: function() {
              alert('Error getting EULA content.');
          }
      });
  });

  $('.modal-content button').click(closeModal);

  ////////////////////// UPLOAD FILE CSS

  $('#uploadBtn', element).click(function(event) {
      event.preventDefault();  // Evitar que el formulario se envíe por defecto
      var handlerUrl = runtime.handlerUrl(element, 'upload_turnitin_submission_file');

      var fileInput = $('#file')[0];
      var file = fileInput.files[0];

      if (!file) {
          alert('Por favor, selecciona un archivo .doc o .docx primero.');
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
              if (response.success) {
                  alert('Archivo subido con éxito a Turnitin.');
              } else {
                  alert('Hubo un error al subir el archivo a Turnitin.');
              }
          },
          error: function() {
              alert('Error comunicándose con el servidor.');
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
              $(this).siblings('label').addClass('file-selected').text('Cambiar archivo');
              uploadButton.prop('disabled', false);
          } else {
              $(this).siblings('.selected-filename').text('Ningún archivo seleccionado');
              $(this).siblings('label').removeClass('file-selected').text('Elegir archivo');
              uploadButton.prop('disabled', true);
          }
      } else {
          alert('Por favor, selecciona un archivo .doc o .docx');
          $(this).val('');
          $(this).siblings('.selected-filename').text('Ningún archivo seleccionado');
          $(this).siblings('label').removeClass('file-selected').text('Elegir archivo');
          uploadButton.prop('disabled', true);
      }
  }
  $('#file', element).on('change', updateSelectedFileName);



//////////////////////////////////////////////////// SIMILARITY

  $('#refreshBtn1', element).click(function(event) {
      event.preventDefault();
      var handlerUrl = runtime.handlerUrl(element, 'get_submission_status');

      $.ajax({
          type: "POST",
          url: handlerUrl,
          data: JSON.stringify({"hello": "world"}),
          success: function(response) {
              updateTrafficLightState('1', response['submission_status']);
          },
          error: function() {
              alert('Error al obtener status de la entrega.');
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
              alert('Successfully scheduled similarity report generation.');
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
              updateTrafficLightState('2', response['report_status']);
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
              alert('Redirecting...');
              openInNewTab(response['viewer_url']);
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
      const refreshBtn2 = document.getElementById(`refreshBtn2`);

      redLight.classList.add('off');
      yellowLight.classList.add('off');
      greenLight.classList.add('off');
      generateReportBtn.disabled = true;
      generateReportBtn.classList.remove('enabled');

      switch (state) {
          case 'ERROR':
              redLight.classList.remove('off');
              break;
          case 'PROCESSING':
              yellowLight.classList.remove('off');
              break;
          case 'COMPLETE':
              greenLight.classList.remove('off');
              generateReportBtn.disabled = false;
              generateReportBtn.classList.add('enabled');
              refreshBtn2.disabled = false;
              refreshBtn2.classList.add('enabled');
              break;
      }
  }

}
