var q0 = document.getElementById('q0');
var q1 = document.getElementById('q1');
var closeButtons = document.getElementsByClassName('remove');
var questions = document.getElementsByClassName('question');
var addButton = document.getElementById('addButton');


var addElement = function(e) {
};

var changeHeading = function(e) {
};

var rmItem = function(e) {
    this.parentElement.parentElement.remove();
};

var addQuestion= function(e) {
};

addButton.addEventListener('click', addQuestion);

for (var i=0; i<removeButtons.length; i++){
	removeButtons[i].addEventListener('click', rmItem);
};

for (var i=0; i<questions.length; i++){
    // highlight questions on mouseover
    questions[i].addEventListener('mouseover',function(){ this.setAttribute("style","outline: 2px dashed black; padding:5px;");});
    questions[i].addEventListener('mouseout', function(){ this.setAttribute("style","outline: 1px solid black; padding:5px;");});


};

console.log(questions);

