$(function(){
	
	var notice = function() {
		alert("Hello");
	};
	
	$("#submitTwiml").on("click", notice);
	
	
	function validate() {
		var submittedTwiml = $("#twiml-box").val();
		var twiml = load("/static/twiml.xsd");
		alert(twiml);
		/*
		var twiml = "hello";
		$.get("/static/twiml.xsd", function(data) {
			twiml = data;
			alert(twiml);
		});*/
	}
});