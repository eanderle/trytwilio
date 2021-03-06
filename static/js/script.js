$(function(){
  /* Fill in phone number at top of screen */
  var phoneOn = false;
  try {
    var phoneNumberLabel = localStorage["phoneNumber"].replace(/(\d{3})(\d{3})(\d{4})/, "($1) $2-$3");
    if (phoneNumberLabel.length==14) {
      $('#phoneNumberDiv').html(phoneNumberLabel);
      $('#phoneToggleButton').button("toggle");
      phoneOn = true;
    }
  } catch(err) {
    $('#browserToggleButton').button("toggle");
  }


  var toggleButtons = function() {
    phoneOn = !phoneOn;
    $('#browserToggleButton').button("toggle");
  };

  $("#phoneToggleButton").on("click", toggleButtons);
  $("#browserToggleButton").on("click", toggleButtons);
  /*
     Twilio Client stuff
     */

  /* Create the Client with a Capability Token */
  var clientToken = $("#token").val();
  Twilio.Device.setup(clientToken);

  /* Let us know when the client is ready. */
  Twilio.Device.ready(function (device) {
    //alert("Ready");
  });

  /* Report any errors on the screen */
  Twilio.Device.error(function (error) {
    //alert("Error: "+ error.message)
  });

  Twilio.Device.connect(function (conn) {
    //alert("Successfully established call")
  });

  /* Connect to Twilio when we call this function. */
  var call = function() {
    var verbType = $("#verb").val();
    var params;
    if (phoneOn == true) {
      params = {
        "verb": verbType,
        "demo": "true",
        "To": localStorage['phoneNumber'],
        "client": "false"
      };
      $.post('/requestCall', 
             params,
             function(data) {
               alert("You should receive a call!");
             }
            );
    } else {
      params = {
        "verb": verbType,
        "To": "",
        "demo": "true",
        "client": "true"
      };
      Twilio.Device.connect(params);
    }

  }

  var hangup = function() {
    Twilio.Device.disconnectAll();
  }

  $('#callButton').on('click', call);

  /*
     Validating TwiML stuff
     */

  var validateTwml = function() {
    var submittedTwiml = editor.getValue();
    var Module = {
      xml: submittedTwiml,
      schema: twimlSchema,
      arguments: ["--noout", "--schema", "file.xsd", "file.xml"]
    };
    var result = validateXML(Module).trim();
    //alert(result);
    var verbType = $("#verb").val();
    if (result == "file.xml validates"){
      var makeCall = $.post('/requestCall', {
        To: "+17863029603",
        twimlBody: submittedTwiml,
        verb: verbType,
        demo: 'false'
      },
      function(data) {
        //alert("Made call:" + data);
      }
                           );
    } else {
      alert("We're sorry. You can't make a call until your TwiML is valid. We have this error: \n" + result);
    }
  };





  var validateTwml = function() {
    var submittedTwiml = editor.getValue();
    var Module = {
      xml: submittedTwiml,
      schema: twimlSchema,
      arguments: ["--noout", "--schema", "file.xsd", "file.xml"]
    };
    var result = validateXML(Module).trim();
    //alert(result);
    var verbType = $("#verb").val();
    if (result == "file.xml validates"){

      if (phoneOn == true) {
        params = {
          "verb": verbType,
          "demo": "false",
          "To": localStorage['phoneNumber'],
          'twimlBody': submittedTwiml,
          "client": "false"
        };
        if(verbType=="gather") {
          params = {
            "verb": verbType,
            "demo": "false",
            "To": localStorage['phoneNumber'],
            'twimlBody': submittedTwiml,
            "twimlBody1": editor2.getValue(),
            "twimlBody2": editor3.getValue(),
            "twimlBody3": editor4.getValue(),
            "client": "false"
          }
        }
        $.post('/requestCall', params,
               function(data) {
                 alert("You should receive a call!");
               }
              );
      } else {
        params = {
          "verb": verbType,
          "demo": "false",
          "To": localStorage['phoneNumber'],
          'twimlBody': submittedTwiml,
          "client": "true"
        };
        if(verbType=="gather") {
          params = {
            "verb": verbType,
            "To": "",
            "demo": "true",
            "client": "true"
          };
        }
        Twilio.Device.connect(params);
      }
    } else {
      alert("We're sorry. You can't make a call until your TwiML is valid. We have this error: \n\n" + result);
    }
  };

  $("#submitTwiml").on("click", validateTwml);

  $('.nav-tabs').button();

  /*
    Registering a new user locally
  */
  function checkDigits(num) {
    num = num.replace(/[^0-9]/g,'');
    return num.length==10;
  }

  var registerPhone = function() {
    var phone = $("#phoneNumber").val().trim();
    if (!checkDigits(phone)) {
      alert("Sorry, your number must contain 10 digits");
      return;
    }
    //alert("good");
    $("#phone-number-register").addClass("disabled");
    $("#phone-number-register").html("Saving...");
    //save it locally
    localStorage['phoneNumber'] = phone;
    localStorage['lesson'] = 'say';
    $("#phone-number-register").html("Saved!");
  }

  $("#phone-number-register").on("click", registerPhone);

  $("#python-link").click(function(){
    setTimeout( function(){
      demoBoxPython.refresh();
      //console.log('editor1 refreshed');
    }, 1);
  });

  $("#php-link").click(function(){
    setTimeout( function(){
      demoBoxPhp.refresh();
      //console.log('editor1 refreshed');
    }, 1);
  });

  $("#gather2").click(function(){
     setTimeout( function(){
       editor2.refresh();
       //console.log('editor1 refreshed');
     }, 1);
   });
   
  $("#gather3").click(function(){
    setTimeout( function(){
      editor3.refresh();
      //console.log('editor1 refreshed');
    }, 1);
  });
  
  $("#gather4").click(function(){
     setTimeout( function(){
       editor4.refresh();
       //console.log('editor1 refreshed');
     }, 1);
   });



  $("#phone-number-form").submit(function(e) {
    e.preventDefault();
  });

  var twimlSchema = '<?xml version="1.0" encoding="iso-8859-1" ?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:annotation><xs:documentation>Twilio API TwiML XML Schema Copyright Twilio Inc.		</xs:documentation></xs:annotation><xs:element name="Response"><xs:complexType><xs:sequence maxOccurs="unbounded" minOccurs="0"><xs:choice><xs:element name="Dial" type="DialType"></xs:element><xs:element name="Gather" type="GatherType"></xs:element><xs:element name="Hangup" type="HangupType"></xs:element><xs:element name="Play" type="PlayType" /><xs:element name="Pause" type="PauseType"></xs:element><xs:element name="Record" type="RecordType"></xs:element><xs:element name="Redirect" type="RedirectType"></xs:element><xs:element name="Reject" type="RejectType"></xs:element><xs:element name="Say" type="SayType"></xs:element><xs:element name="Sms" type="SmsType"></xs:element></xs:choice></xs:sequence><xs:attribute name="version" type="xs:string"></xs:attribute></xs:complexType></xs:element><xs:complexType name="PlayType"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="loop" type="xs:int"></xs:attribute></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="SayType" mixed="true"><xs:attribute name="loop" type="xs:int"></xs:attribute><xs:attribute name="voice" type="voiceType"></xs:attribute><xs:attribute name="language" type="xs:string"></xs:attribute></xs:complexType><xs:complexType name="GatherType"><xs:sequence maxOccurs="unbounded" minOccurs="0"><xs:choice><xs:element name="Play" type="PlayType"></xs:element><xs:element name="Say" type="SayType"></xs:element><xs:element name="Pause" type="PauseType"></xs:element></xs:choice></xs:sequence><xs:attribute name="numDigits" type="xs:int"></xs:attribute><xs:attribute name="finishOnKey" type="xs:string"></xs:attribute><xs:attribute name="method" type="methodType"></xs:attribute><xs:attribute name="action" type="xs:string"></xs:attribute><xs:attribute name="timeout" type="xs:int"></xs:attribute></xs:complexType><xs:simpleType name="methodType"><xs:restriction base="xs:string"></xs:restriction></xs:simpleType><xs:complexType name="DialType" mixed="true"><xs:sequence maxOccurs="unbounded" minOccurs="0"><xs:choice><xs:element name="Number" type="NumberType"></xs:element><xs:element name="Client" type="ClientType"></xs:element><xs:element name="Conference" type="conferenceType"></xs:element></xs:choice></xs:sequence><xs:attribute name="action" type="xs:string"></xs:attribute><xs:attribute name="callerId" type="xs:string"></xs:attribute><xs:attribute name="hangupOnStar" type="xs:string"></xs:attribute><xs:attribute name="method" type="methodType"></xs:attribute><xs:attribute name="record" type="xs:string"></xs:attribute><xs:attribute name="timeLimit" type="xs:int"></xs:attribute><xs:attribute name="timeout" type="xs:int"></xs:attribute><xs:attribute name="transcribe" type="xs:string"></xs:attribute><xs:attribute name="transcribeCallback" type="xs:string"></xs:attribute></xs:complexType><xs:complexType name="NumberType"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="sendDigits" type="xs:string"></xs:attribute><xs:attribute name="url" type="xs:string"></xs:attribute></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="ClientType"><xs:simpleContent><xs:extension base="xs:string"></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="RecordType"><xs:attribute name="action" type="xs:string"></xs:attribute><xs:attribute name="finishOnKey" type="xs:string"></xs:attribute><xs:attribute name="maxLength" type="xs:int"></xs:attribute><xs:attribute name="method" type="methodType"></xs:attribute><xs:attribute name="playBeep" type="xs:string"></xs:attribute><xs:attribute name="timeout" type="xs:int"></xs:attribute><xs:attribute name="transcribe" type="xs:string"></xs:attribute><xs:attribute name="transcribeCallback" type="xs:string"></xs:attribute></xs:complexType><xs:simpleType name="voiceType"><xs:restriction base="xs:string"><xs:enumeration value="man"></xs:enumeration><xs:enumeration value="woman"></xs:enumeration></xs:restriction></xs:simpleType><xs:simpleType name="reasonType"><xs:restriction base="xs:string"><xs:enumeration value="busy"></xs:enumeration><xs:enumeration value="rejected"></xs:enumeration></xs:restriction></xs:simpleType><xs:simpleType name="HangupType"><xs:restriction base="xs:string"></xs:restriction></xs:simpleType><xs:complexType name="PauseType"><xs:attribute name="length" type="xs:int"></xs:attribute></xs:complexType><xs:simpleType name="langType"><xs:restriction base="xs:string"><xs:enumeration value="en"></xs:enumeration><xs:enumeration value="es"></xs:enumeration><xs:enumeration value="fr"></xs:enumeration><xs:enumeration value="de"></xs:enumeration></xs:restriction></xs:simpleType><xs:complexType name="RedirectType"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="method" type="methodType"></xs:attribute></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="conferenceType"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="beep" type="xs:string"></xs:attribute><xs:attribute name="endConferenceOnExit" type="xs:string"></xs:attribute><xs:attribute name="maxParticipants" type="xs:string"></xs:attribute><xs:attribute name="method" type="methodType"></xs:attribute><xs:attribute name="muted" type="xs:string"></xs:attribute><xs:attribute name="startConferenceOnEnter" type="xs:string"></xs:attribute><xs:attribute name="url" type="xs:string"></xs:attribute><xs:attribute name="waitMethod" type="xs:string"></xs:attribute><xs:attribute name="waitUrl" type="xs:string"></xs:attribute></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="SmsType"><xs:simpleContent><xs:extension base="xs:string"><xs:attribute name="from" type="xs:string"></xs:attribute><xs:attribute name="to" type="xs:string"></xs:attribute><xs:attribute name="action" type="xs:string"></xs:attribute><xs:attribute name="method" type="methodType"></xs:attribute><xs:attribute name="statusCallback" type="xs:string"></xs:attribute></xs:extension></xs:simpleContent></xs:complexType><xs:complexType name="RejectType"><xs:attribute name="reason" type="reasonType"></xs:attribute></xs:complexType></xs:schema>';
});
