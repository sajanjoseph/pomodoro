$(document).ready(function(){
	$('#slider').slider({ 
	    min:1,
	    max:10,
	    step:1,
	    value:5,
	    
	    
	    change : function (e, ui) {
	        $('#id_difficulty').val(ui.value);
	    },
	    
	    create:  function(e, ui){ $('#id_difficulty').val(5);}
	  
	   });
	
	
});