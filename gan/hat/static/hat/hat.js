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

;(function($) {
    $.fn.textfill = function(options) {
        var fontSize = options.maxFontPixels;
        var ourText = $('span:visible:first', this);
        var maxHeight = $(this).height();
        var maxWidth = $(this).width();
        var textHeight;
        var textWidth;
        do {
            ourText.css('font-size', fontSize);
            textHeight = ourText.height();
            textWidth = ourText.width();
            fontSize = fontSize - 1;
        } while ((textHeight > maxHeight || textWidth > maxWidth) && fontSize > 3);
        return this;
    }
})(jQuery);

$(document).ready(function(){
  setTimeout(fetchdata,2000);
  
  if ($("#word").length)
    $('#word').textfill({ maxFontPixels: 36 })
  
  if ($("#historyword").length)
    $('#historyword').textfill({ maxFontPixels: 36 })
    
  //if ($("#audiotag").length)
  //  document.getElementById('audiotag').play();
});