function showEntriesList(){
	var block1toshow = document.getElementById("users_selected");
    var blocktoshow = document.getElementById("some_entries_selected");
    var blocktohide = document.getElementById("categories_selected");
    blocktoshow.style.display="block";
    block1toshow.style.display="block";
    blocktohide.style.display="none";
}
function showCategories(){
	var block1toshow = document.getElementById("users_selected");
    var blocktoshow = document.getElementById("categories_selected");
    var blocktohide = document.getElementById("some_entries_selected");
    block1toshow.style.display="block";
    blocktoshow.style.display="block";
    blocktohide.style.display="none";
}

function hideAll(){
	var block1toshow = document.getElementById("users_selected");
    var block1tohide = document.getElementById("some_entries_selected");
    var block2tohide = document.getElementById("categories_selected");
    block1toshow.style.display="block";
    block1tohide.style.display="none";
    block2tohide.style.display="none";
}
