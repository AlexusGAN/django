function fetchdata(){
 $.getJSON("ajax", function(data) {
   if ($("#timer").length)
    $("#timer").val(data['progress']);
   else if (data['progress'] > 0 && data['progress'] < 100)
   {
      location.reload();
      return;
   }
   
   if (data['progress'] >= 100 && $("form").length ) {
     $( "#form" ).submit();
   }
   
   if (turn_number != data['turn_number'] || grades != data['grades'] || game_state != data['game_state'])
      location.reload();
   else
      setTimeout(fetchdata,2000);
 });
}

$(document).ready(function(){
 setTimeout(fetchdata,2000);
});