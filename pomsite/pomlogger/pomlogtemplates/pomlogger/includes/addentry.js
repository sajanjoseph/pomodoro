var start_d;
var stop_d;
function initpage(){
    //alert('initpage()');
    start_d=new Date();
    setInterval(showtime,1000);
    
    var begin_timestr=start_d.toLocaleTimeString();
    var timerstartedfield = document.getElementById("timerstartedfld");
    timerstartedfield.innerHTML=begin_timestr;
    document.timeform.timerstarted.value=begin_timestr;
        
}
function showform(){
    block=document.getElementById("entrydata");
    block.style.display="block";
}
function hideform(){
    block=document.getElementById("entrydata");
    block.style.display="none";
}
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


function showtime(){
    var currenttimefield = document.getElementById("currenttime");
    timebtnvalue=document.timeform.timebtn.getAttribute("value")
    if (timebtnvalue=="stop"){
        currenttimefield.innerHTML=new Date().toLocaleTimeString();
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

