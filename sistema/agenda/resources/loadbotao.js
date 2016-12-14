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
  
function desabilitaCaixaTexto(obj) {      
	var ultimo=obj.id.substring(obj.id.length-1);
	var campo=obj.id.substring(13,obj.id.length-2);	
	var idTexto = "formfield-form-widgets-detalhes"+campo;
	var idResponsavel = "formfield-form-widgets-responsavel"+campo;
	var idSetor = "formfield-form-widgets-setor"+campo;
	var idEmail = "formfield-form-widgets-email"+campo;
	var idCelular = "formfield-form-widgets-celular"+campo;
	var idFixo = "formfield-form-widgets-fixo"+campo;
	try{
		var campoTexto = document.getElementById(idTexto); 
		var campoResponsavel = document.getElementById(idResponsavel); 
		var campoSetor = document.getElementById(idSetor); 
		var campoEmail = document.getElementById(idEmail); 
		var campoCelular = document.getElementById(idCelular); 
		var campoFixo = document.getElementById(idFixo); 
		if (ultimo=="0"){
			if (campoTexto!==null)
				campoTexto.style.display = "block";		
		    if (campoResponsavel!==null)
				campoResponsavel.style.display = "block";		
			if (campoSetor!==null)
				campoSetor.style.display = "block";		
			if (campoEmail!==null)
				campoEmail.style.display = "block";		
			if (campoCelular!==null)
				campoCelular.style.display = "block";		
			if (campoFixo!==null)
				campoFixo.style.display = "block";		
		}
		else{		
			if (campoTexto!==null)
				campoTexto.style.display = "none";		
		    if (campoResponsavel!==null)
				campoResponsavel.style.display = "none";		
			if (campoSetor!==null)
				campoSetor.style.display = "none";		
			if (campoEmail!==null)
				campoEmail.style.display = "none";		
			if (campoCelular!==null)
				campoCelular.style.display = "none";		
			if (campoFixo!==null)
				campoFixo.style.display = "none";	
		}    
	}catch(err){
		alert(err.message+" - "+campo);
	}

}
  
  
   