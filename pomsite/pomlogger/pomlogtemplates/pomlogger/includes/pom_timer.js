$(document).ready(function(){

//instead of Date.toLocaleTimeString());
//use d.toUTCString());
//or use date.getTime() to return milliseconds since epoch


var showtime=function(){
    
    var timebtnvalue=$('#timebtn').attr("value");
    //alert('showtime:timebtnvalue='+timebtnvalue);
    if (timebtnvalue=="stop"){
        $('#currenttime').html(new Date().toLocaleTimeString());
        //alert('put new date');
    }
};


var changeBtnStatus=function(){
    var timebtnvalue=$('#timebtn').attr("value");
    var timebtnimg=$('#btnimg');
    if (timebtnvalue =="start"){
        $('#timebtn').attr("value","stop");
        timebtnimg.attr('src','{{ MEDIA_URL }}img/Stop1.png');
        
        hideElement("entrydata");
        var start_date=new Date();
        var str_time=start_date.toLocaleTimeString();
        var start_time_millis = start_date.getTime()//get millis
        var timerstartedfield =$('#timerstarted');
        var timerstartedshowfield =$('#start_time_show');
        timerstartedshowfield.html(str_time);
        //timerstartedfield.attr("value",str_time);
        timerstartedfield.attr("value",start_time_millis);
        
        var startshowfield =$('#start_time_show_always');
        showElement("start_time_show_always");
        startshowfield.html("timer started at :"+str_time);
        
       
       
    }
    else if (timebtnvalue=="stop"){
        $('#timebtn').attr("value","start");
        timebtnimg.attr('src','{{ MEDIA_URL }}img/Play1.png');
        
        hideElement("ctimefld");
        var stop_date=new Date();
        var stp_time=stop_date.toLocaleTimeString();
        var stp_time_millis = stop_date.getTime();
        
        var timerstoppedfield =$('#timerstopped');
        timerstoppedfield.attr("value",stp_time_millis);
        var timerstoppedshowfield =$('#stop_time_show');
        timerstoppedshowfield.html(stp_time);
        //alert('stop time set as'+stp_time_millis);
        hideElement("start_time_show_always");
        showElement("entrydata");
    }
};


var timerBtnClicked=function(){
    
    showElement("ctimefld");
    setInterval(showtime,1000);
    changeBtnStatus();
    };
var showElement=function(elementId){
    var elem_selector='#'+elementId;
    $(elem_selector).show();
    
};
var hideElement=function(elementId){
    var elem_selector='#'+elementId;
    $(elem_selector).hide();
   
};

var display_error_inline=function(msg,elemId){
    var msg_elem = $('<i>'+msg+'</i><br/>');
    elem_selector='#'+elemId;
    var elem=$(elem_selector);
    msg_elem.insertAfter(elem).fadeIn('slow').animate({opacity: 1.0}, 5000).fadeOut('slow',function() { msg_elem.remove(); });
    
};

var validate=function(){
    
    var desc_ok=true;
    var cat_ok=true;
    var categories=$("#id_categories").val();
    var description=$("#id_description").val();
    if (description.length==0){
        display_error_inline('description should not be empty','id_description');
        showElement("entrydata");
        desc_ok=false;
    }
    if ((categories.length==0 )){
        display_error_inline('category should not be empty','id_categories');
        showElement("entrydata");
        cat_ok=false;
        
    }
    
    if (desc_ok & cat_ok){
        return true;
    }
    
    else{
        return false;
    }
};


$('#timebtn').click(timerBtnClicked);
$('#timeform').submit(validate);

//$('#timeform').attr('onsubmit',validate);
}//all encompassing function
);
