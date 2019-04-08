$(document).on('show.bs.modal', function(event){
  var button = $(event.relatedTarget);
  var nodeID = button.data('commid');
  var modal = $(this);
  makeRequest(nodeID);
  // response_area = document.getElementById("test-response");
  // modal.find('#question-body-content').text(nodeID);
});


var httpRequest;
// var response_area;
// $(document).ready(function(){
//   console.log("getting it");
//   var button = $(event.relatedTarget);
//   var nodeID = button.data('commid');
//   var question_url = "https://community.clover.com/services/v2/question/" + str(nodeID) + ".json"

//   document.getElementById('test-button').addEventListener('click', makeRequest)
//   response_area = document.getElementById("test-response")
// });

function makeRequest(nodeID){
  httpRequest = new XMLHttpRequest();
  httpRequest.withCredentials = true;
  var question_url = "https://community.clover.com/services/v2/question/" + nodeID + ".json"


  if (!httpRequest){
    console.log("nah")
    $('#test-response').text("something went wrong");
    return false;
  }

  httpRequest.onreadystatechange = alertContents;
  httpRequest.open(
    'GET', question_url
    );
  httpRequest.send();
}

function alertContents(){
  if (httpRequest.readyState === XMLHttpRequest.DONE){
    if (httpRequest.status === 200){
      console.log("success")
      $('#question-body-content').text(JSON.parse(httpRequest.responseText).body);
    } else {
      console.log("nope");
      $('#question-body-content').text("nope");
    }
  }
}