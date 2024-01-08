$(document).ready(function() {
    $('.form-container').submit(function(event) {  //registration
        event.preventDefault(); // Prevent the default form submission
        // Get form data
        var formData = {
            qty: $('#qty').val()
        }; 
        spinner("show")
        // Send POST request using AJAX
        $.ajax({
            type: 'POST',
            url: '/', // Update with your server endpoint
            data: formData,
            success: function(response) {
                spinner("hide")
                redirect(response)  
            },
            error: function(error) {
                spinner("hide")
                console.error('Error sending data:', error);
            }
        });
    });
});

function redirect(res){
  var options = {
      "key": res['RZPAY_ID'],
      "amount": res['amount'],
      "currency": res['currency'],
      "name": res['COMPANY_NAME'], //your business name
      "description": res['DESCRIPTION'],
      "image": "https://www.freelancer.in/contest/catchy-logo-design-for-mst-565076-byentry-9582403",
      "order_id": res['id'],
      // "callback_url": `https://aade-2409-40d7-a-a9f1-363a-315d-2f88-adeb.ngrok-free.app`,
      "prefill": {
          "name": res['notes']['name'],
          "email": res['notes']['email'],
          "contact": res['notes']['contact']
      },
      "notes": {
          "address": res['ADDRESS']
      },
      "theme": {
          "color": "#eab676"
      },
      "handler": function (response){
          var formData = {
            razorpay_payment_id:response.razorpay_payment_id, 
            razorpay_order_id:response.razorpay_order_id,
            razorpay_signature:response.razorpay_signature,
          }; 
          spinner("show")
          $.ajax({
              type: 'POST',
              url: '/verify',
              data: formData,
              success: function(response) {
                  if (response['msg']!== false ){
                    window.location.href= response
                    spinner("hide")
                  }
              },
              error: function(error) {
                spinner("hide")
                  console.error('Error sending details:', error);
              }
          });
      },
      };
  var rzp1 = new Razorpay(options);
  rzp1.open();
}

function spinner(val) {
  if (val == "show") {
    $('#loadingSpinner').removeClass('d-none');
  } else if (val == "hide") {
    $('#loadingSpinner').addClass('d-none');
  }
}