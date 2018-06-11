var questionList = document.getElementById('questionList');
var removeButtons = document.getElementsByClassName('remove');
var questions = document.getElementsByClassName('question');
var answerDivs = document.getElementsByClassName('answer');
var dropdowns = document.getElementsByClassName('select');
var addButton = document.getElementById('addButton');

var removeQuestion = function(e) {
    // removes list item containing the parent div
    
    var parentDiv = this.parentElement.parentElement;
    var index = this.parentElement.getAttribute('name');
    parentDiv.remove();
    console.log(index);
    // decrements all the following question numbers
    for (var i = index; index < questionList.length; i++){
        // reset all names
    };
};

var addQuestion= function(e) {
    var questionNumber = questions.length;
    var newQuestion = document.createElement('li');
    questionList.appendChild(newQuestion);
    
    var questionDiv = document.createElement('div');
    newQuestion.appendChild(questionDiv);
    questionDiv.setAttribute('class', 'question');
    questionDiv.setAttribute('style','outline: 1px solid black; padding: 5px;  margin-bottom: 15px;');
    questionDiv.setAttribute('name', questionNumber);
    questionDiv.addEventListener('mouseover', function(){this.setAttribute('style','outline: 2px dashed black; padding: 5px; margin-bottom: 15px;');});
    questionDiv.addEventListener('mouseout', function(){this.setAttribute('style','outline: 1px solid black; padding: 5px; margin-bottom: 15px;');});
        
    var newRemove = document.createElement('button');
    questionDiv.appendChild(newRemove);
    newRemove.setAttribute('type', 'button');
    newRemove.setAttribute('class', 'remove');
    newRemove.setAttribute('style', 'position: relative; top:0; float: right;');
    newRemove.innerHTML = 'X';
    // newRemove.addEventListener('click', removeQuestion); // does not work for some reason
    for (var i=0; i<removeButtons.length; i++){
        removeButtons[i].addEventListener('click', removeQuestion); // workaround for above eventlistener not working
    };
    
    questionDiv.innerHTML+='Question:';
    var newQuestionBox = document.createElement('input');
    questionDiv.appendChild(newQuestionBox);
    questionDiv.appendChild(document.createElement('br'));
    newQuestionBox.setAttribute('type', 'text');
    newQuestionBox.setAttribute('name', questionNumber + '.question');
    
    questionDiv.innerHTML+='Question Type:';
    var newDropdown = document.createElement('select');
    newDropdown.selectedIndex = -1;
    newDropdown.setAttribute('class', 'select');
    newDropdown.setAttribute('name', questionNumber + '.type');
    var questionTypes = ['one-line response', 'extended response', 'numerical', 'multiple-choice'];
    for (var i = 0; i < questionTypes.length; i++){
        var questionTypeOption = document.createElement('option');
        questionTypeOption.setAttribute('value', i);
        questionTypeOption.innerHTML = questionTypes[i];
        newDropdown.appendChild(questionTypeOption);
    };
    questionDiv.appendChild(newDropdown);
    questionDiv.appendChild(document.createElement('br'));
    
    questionDiv.innerHTML+="Required? "
    var requiredBox = document.createElement('input');
    requiredBox.setAttribute('type', 'checkbox');
    requiredBox.setAttribute('name', questionNumber + '.required');
    questionDiv.appendChild(requiredBox);
    
    var answerDiv = document.createElement('div');
    answerDiv.setAttribute('class', 'answer');
    questionDiv.appendChild(answerDiv);
    
    // dynamic answer selection based on question type
    for (var i = 0; i<dropdowns.length; i++){
        dropdown = dropdowns[i];
        dropdown.onchange = function() {
            if (dropdown.value=="0" || dropdown.value=="1"){ // text responses
                while (answerDiv.firstChild) answerDiv.removeChild(answerDiv.firstChild);
                answerDiv.innerHTML+='Min. characters: ';
                var minBox = document.createElement('input');
                minBox.setAttribute('type', 'text');
                minBox.setAttribute('name', questionNumber + '.min');
                minBox.setAttribute('maxlength', '4');
                minBox.setAttribute('size', '3');
                answerDiv.appendChild(minBox);
                answerDiv.innerHTML+='Max. characters: ';
                var maxBox = document.createElement('input');
                maxBox.setAttribute('type', 'text');
                maxBox.setAttribute('name', questionNumber + '.max');
                maxBox.setAttribute('maxlength', '4');
                maxBox.setAttribute('size', '3');
                answerDiv.appendChild(maxBox);
            } 
            else if (dropdown.value == "2"){ // numerical
                while (answerDiv.firstChild) answerDiv.removeChild(answerDiv.firstChild);
                answerDiv.innerHTML+='Min. number: ';
                var minBox = document.createElement('input');
                minBox.setAttribute('type', 'text');
                minBox.setAttribute('name', questionNumber + '.min');
                minBox.setAttribute('maxlength', '2');
                minBox.setAttribute('size', '1');
                answerDiv.appendChild(minBox);
                answerDiv.innerHTML+='Max. number: ';
                var maxBox = document.createElement('input');
                maxBox.setAttribute('type', 'text');
                maxBox.setAttribute('name', questionNumber + '.max');
                maxBox.setAttribute('maxlength', '5');
                maxBox.setAttribute('size', '3');
                answerDiv.appendChild(maxBox);
            } 
            else if (dropdown.value == "3"){ // multiple-choice
                while (answerDiv.firstChild) answerDiv.removeChild(answerDiv.firstChild);
                answerDiv.appendChild(document.createElement('input'));
                // add expandable list of possible choices here
                
            } else {while (answerDiv.firstChild) answerDiv.removeChild(answerDiv.firstChild);};
        };
    };
};

addButton.addEventListener('click', addQuestion);

for (var i=0; i<removeButtons.length; i++){
	removeButtons[i].addEventListener('click', removeQuestion);
};

for (var i=0; i<questions.length; i++){
    // highlight questions on mouseover
    questions[i].addEventListener('mouseover',function(){ this.setAttribute("style","outline: 2px dashed black; padding: 5px; margin-bottom: 15px;");});
    questions[i].addEventListener('mouseout', function(){ this.setAttribute("style","outline: 1px solid black; padding: 5px; margin-bottom: 15px;");});
};
