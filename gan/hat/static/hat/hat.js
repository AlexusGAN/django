var count = 0;

function fetchdata(){
  //Покажем кнопку угадал. Сразу не видно, чтобы не жали случайно на медленных смартфонах
  if (count == 0 && $("#action").length)
  {
    $('#action').show();
    $('#action').prop('disabled', false);
  }
  
  //Не дадим забытым играм вечно теребить сервер
  if (count++ >= 120)
  {
    if ($("#action").length)
      $('#action').hide(); 
    $('#continue').show();
    return;
  }

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
      setTimeout(fetchdata,1000);
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
  setTimeout(fetchdata,1000);

  if ($("#form").length)
    $("#form").submit(function(data) {
      $('#action').hide(); $('#action2').show();
    })
  
  if ($("#word").length)
    $('#word').textfill({ maxFontPixels: 36 })
  
  if ($("#historyword").length)
    $('#historyword').textfill({ maxFontPixels: 36 })
});