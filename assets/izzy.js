$(document).on('show.bs.modal', function(event){
  // Quick View; Grabs the body of the question based on the ID
  var button = $(event.relatedTarget);
  var nodeID = button.data('commid');
  var modal = $(this);
  makeRequest(nodeID);
});

var httpRequest;

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