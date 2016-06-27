  $(function() {
    $("input").on( "click", function( event ) {  
	  var target = $(event.target); 

	  
      if (target.is("#form-buttons-enviar") ) {        
        var progressbar = $( "#progressbar" ),
        progressLabel = $( ".progress-label" );
 
        progressbar.progressbar({
          value: false,	  
          change: function() {
            progressLabel.text( progressbar.progressbar( "value" ) + "%" );
          },
          complete: function() {
            progressLabel.text( "Melhor solução encontrada! Aguarde a finalização." );
          }
        });
 
        function progress() {
          var val = progressbar.progressbar( "value" ) || 0;
 
          progressbar.progressbar( "value", val + 1 );
 
          if ( val < 99 ) {
            setTimeout( progress, 800 );
          }
        }
 
        setTimeout( progress, 2000 );
      } 
    
	});
	
  });
  
   