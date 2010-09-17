var start_d;
var stop_d;
function initpage(){
    //alert('initpage()');
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
    
    //var begin_timestr=start_d.toLocaleTimeString();
    //var timerstartedfield = document.getElementById("timerstartedfld");
    //timerstartedfield.innerHTML=begin_timestr;
    //document.timeform.timerstarted.value=begin_timestr;
    
        
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
    //block=document.getElementById("entrydata");
    //block.style.display="block";
    $('#entrydata').show();
}
function hideform(){
    //block=document.getElementById("entrydata");
    //block.style.display="none";
    $('#entrydata').hide();
}

/*
function changeBtnStatus(){
    timebtnvalue=document.timeform.timebtn.getAttribute("value")
    //alert('timebtnvalue='+timebtnvalue);
    if (timebtnvalue=="start"){
        
        document.timeform.timebtn.setAttribute("value","stop");
        start_d=new Date();
        var start_date=start_d;
        var str_time=start_date.toLocaleTimeString();
        var timerstartedfield = document.getElementById("timerstartedfld");
        timerstartedfield.innerHTML=str_time;
        document.timeform.timerstarted.value=str_time;
        hideform();
        //alert('set timerstartedfield='+str_time);
        
    }
    else if (timebtnvalue=="stop"){
        document.timeform.timebtn.setAttribute("value","start");
        var stop_date=new Date();
        stop_d=stop_date;
        var stp_time=stop_date.toLocaleTimeString();
        var timerstoppedfield = document.getElementById("timerstoppedfld");
        timerstoppedfield.innerHTML=stp_time;
        document.timeform.timerstopped.value=stp_time;
        //alert('set timerstoppedfield='+stp_time);
        showform();
    }
    
}
*/

function changeBtnStatus(){
    //alert("changeBtnStatus()::");
    var timebtnvalue=$('#timebtn').attr("value");
    //var timebtnimg=$('#btnimg');
    //alert('changeBtnStatus()::timebtnvalue='+timebtnvalue);
    //alert('changeBtnStatus()::timebtnimg='+timebtnimg);
    if (timebtnvalue =="start"){
        $('#timebtn').attr("value","stop");
        //timebtnimg.attr('src','{{ MEDIA_URL }}img/Stop1.png');
        
        
        /*alert('changed buttonimg to stop png') */
        hideElement("entrydata");
        start_d=new Date();
        var start_date=start_d;
        var str_time=start_date.toLocaleTimeString();
        var timerstartedfield =$('#timerstartedfld');
        var timerstartedhiddenfield =$('#timerstarted');
        timerstartedfield.html(str_time);
        alert('start fld set to:'+str_time);
        timerstartedhiddenfield.attr("value",str_time);
        alert('start hiddenfield set to:'+str_time);
        
        
        /*alert('start time set as'+str_time);*/
        //alert('timerstartedhiddenfield.attr("value")='+timerstartedhiddenfield.attr("value"));
    }
    else if (timebtnvalue=="stop"){
        $('#timebtn').attr("value","start");
        //timebtnimg.attr('src','{{ MEDIA_URL }}img/Play1.png');
        /*alert('changed buttonimg to start png');*/
        hideElement("currenttimediv");
        var stop_date=new Date();
        stop_d=stop_date;
        var stp_time=stop_date.toLocaleTimeString();
        
        var timerstoppedhiddenfield =$('#timerstopped');
        timerstoppedhiddenfield.attr("value",stp_time);
        var timerstoppedshowfield =$('#timerstoppedfld');
        timerstoppedshowfield.html(stp_time);
        alert('timerstoppedshowfield set as :'+stp_time);
        alert('stop hiddenfield set to:'+stp_time);
        alert('stop hiddenfield is:'+timerstoppedhiddenfield.attr("value"));
        
        /*alert('stop time set as='+stp_time);*/
        //alert('timerstoppedhiddenfield.attr("value")='+timerstoppedhiddenfield.attr("value"));
        showElement("entrydata");
    }
    
}


function showtime(){
    /*
    var currenttimefield = document.getElementById("currenttime");
    timebtnvalue=document.timeform.timebtn.getAttribute("value")
    if (timebtnvalue=="stop"){
        currenttimefield.innerHTML=new Date().toLocaleTimeString();
        
    }
    */
    
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
/*
    start_time=start_d;
    stop_time=stop_d;
    if (start_time < stop_time){
        return true;
    }
    else{
        alert('start_time'+start_time+ 'must be < stop_time'+stop_time);
        
        return false;
    }
*/
}
function isNotEmpty(elem) {
    var str = elem.value;
    //alert('isNotEmpty() str='+str);
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

