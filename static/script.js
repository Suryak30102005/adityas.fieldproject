$(document).ready(function(){
    $('#download-form').on('submit', function(e){
      e.preventDefault();
      var url = $('#url-input').val();
      var brand = $('#brand-select').val();
      showNotification('Processing your download request...', 'info');
  
      $.ajax({
        type: 'POST',
        url: '/download',
        data: { url: url, brand: brand },
        success: function(response) {
          if(response.status === 'success') {
            showNotification(response.message, 'success');
            // Trigger file download via an invisible anchor element
            var a = document.createElement('a');
            a.href = response.download_url;
            a.download = '';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            $('#url-input').val('');
          } else {
            showNotification(response.message, 'error');
          }
        },
        error: function(xhr) {
          var errorMsg = xhr.responseJSON ? xhr.responseJSON.message : 'Server error';
          showNotification('Error: ' + errorMsg, 'error');
        }
      });
    });
  
    // Show notifications with fade effects
    function showNotification(message, type) {
      var notification = $('#notification');
      notification.removeClass().addClass('notification ' + type).text(message).fadeIn(500);
      setTimeout(function(){
        notification.fadeOut(500);
      }, 3000);
    }
  });
  
  // Hamburger menu functions
  function openNav() {
    document.getElementById("mySidenav").style.left = "0";
  }
  function closeNav() {
    document.getElementById("mySidenav").style.left = "-250px";
  }
  