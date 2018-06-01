var question = document.getElementById('q0');
var theButton = q0.getElementById('q0b');
var ans = seqList.getElementsByTagName('li');

var addElement = function(e) {
};

var changeHeading = function(e) {
};

var rmItem = function(e) {    
    this.remove();
};

theButton.addEventListener('click', rmItem);

for (var i=0;i<listItem.length;i++){
    listItem[i].addEventListener('mouseover', changeHeading);
    listItem[i].addEventListener('mouseout', revertHeading);
    listItem[i].addEventListener('click', rmItem);
};
