var start_d;
var stop_d;
function initpage(){
    start_d=new Date();
    var str_time=start_d.toLocaleTimeString();
    var timerstartedfield =$('#timerstartedfld');
    var timerstartedhiddenfield =$('#timerstarted');
    timerstartedfield.html(str_time);
    alert('start fld set to:'+str_time);
    timerstartedhiddenfield.attr("value",str_time);
    alert('start hiddenfield set to:'+str_time);
    
    showElement("currenttimediv");
    setInterval(showtime,1000);
}

function showElement(elementId){
    var elem_selector='#'+elementId;
    $(elem_selector).show();
}
function hideElement(elementId){
    var elem_selector='#'+elementId;
    $(elem_selector).hide();
}

function showform(){
    $('#entrydata').show();
}
function hideform(){
    $('#entrydata').hide();
}



function changeBtnStatus(){
    var timebtnvalue=$('#timebtn').attr("value");
    if (timebtnvalue =="start"){
        $('#timebtn').attr("value","stop");
        
        hideElement("entrydata");
        start_d=new Date();
        var start_date=start_d;
        var str_time=start_date.toLocaleTimeString();
        var timerstartedfield =$('#timerstartedfld');
        var timerstartedhiddenfield =$('#timerstarted');
        timerstartedfield.html(str_time);
        alert('javascript:start hidden fld set to:'+str_time);
        timerstartedhiddenfield.attr("value",str_time);
        alert('javascript:start hiddenfield set to:'+str_time);
        
    }
    else if (timebtnvalue=="stop"){
        $('#timebtn').attr("value","start");
        hideElement("currenttimediv");
        var stop_date=new Date();
        stop_d=stop_date;
        var stp_time=stop_date.toLocaleTimeString();
        
        var timerstoppedhiddenfield =$('#timerstopped');
        timerstoppedhiddenfield.attr("value",stp_time);
        var timerstoppedshowfield =$('#timerstoppedfld');
        timerstoppedshowfield.html(stp_time);
        
        showElement("entrydata");
    }
    
}


function showtime(){
    var timebtnvalue=$('#timebtn').attr("value");
    $('#currenttimediv').show();
    if (timebtnvalue=="stop"){
        $('#currenttime').html(new Date().toLocaleTimeString());
    }
}

function validateForm(form){
    alert('validateForm()');
    var desc=form.description;
    var cat=form.categories;
    if (isNotEmpty(desc) && isNotEmpty(cat)) {
        return true;
    } 
    else{   
        return false;
    }

}
function isNotEmpty(elem) {
    var str = elem.value;
    if(str == null || str.length == 0) {
        alert("Please fill in the required field.");
        return false;
    } else {
        return true;
    }
}

function display_error_inline(msg,elemId){
    var msg_elem = $('<i>'+msg+'</i><br/>');
    elem_selector='#'+elemId;
    var elem=$(elem_selector);
    msg_elem.insertAfter(elem).fadeIn('slow').animate({opacity: 1.0}, 5000).fadeOut('slow',function() { msg_elem.remove(); });
}
function display_error(msg,elemId){
    var msg_div = $('<div class="error_message"><p>'+msg+'</p></div>');
    elem_selector='#'+elemId;
    var elem=$(elem_selector);
    msg_div.insertAfter(elem).fadeIn('slow').animate({opacity: 1.0}, 5000).fadeOut('slow',function() { msg_div.remove(); });
}

