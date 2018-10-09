var questionList = document.getElementById('questionList');
var removeButtons = document.getElementsByClassName('remove');
var questions = document.getElementsByClassName('question');
var answerDivs = document.getElementsByClassName('answer');
var dropdowns = document.getElementsByClassName('select');
var addButton = document.getElementById('addButton');

var dynamicAnswer = function(e){
    // dynamic answer selection based on question type
    for (var i = 0; i < dropdowns.length; i++){
        drop = dropdowns[i];
        let index = i;
        var dropdown = drop;
        setTimeout(function(){
            dropdown.onchange = function(){
                //console.log("parent is " + dropdown.parentElement.getAttribute('name'));
                //console.log('looking at ' + index);
                answer = dropdown.parentElement.parentElement.getElementsByClassName("answer")[0];
                if (dropdown.value=="0" || dropdown.value=="1"){ // text responses
                    while (answer.firstChild) answer.removeChild(answer.firstChild);
                    answer.innerHTML+='(Optional) Min. characters: ';
                    var minBox = document.createElement('input');
                    minBox.setAttribute('type', 'number');
                    minBox.setAttribute('min', '0');
                    minBox.setAttribute('name', index + '.min');
                    minBox.setAttribute('maxlength', '4');
                    minBox.setAttribute('size', '3');
                    answer.appendChild(minBox);
                    answer.appendChild(document.createElement('br'));
                    answer.innerHTML+='(Optional) Max. characters: ';
                    var maxBox = document.createElement('input');
                    maxBox.setAttribute('type', 'number');
                    maxBox.setAttribute('min', '0');
                    maxBox.setAttribute('name', index + '.max');
                    maxBox.setAttribute('maxlength', '4');
                    maxBox.setAttribute('size', '3');
                    answer.appendChild(maxBox);
                } 
                else if (dropdown.value == "2" || dropdown.value == "3"){ // numerical
                    while (answer.firstChild) answer.removeChild(answer.firstChild);
                    answer.innerHTML+='Min. number: ';
                    var minBox = document.createElement('input');
                    minBox.setAttribute('type', 'number');
                    minBox.setAttribute('name', index + '.min');
                    minBox.setAttribute('maxlength', '2');
                    minBox.setAttribute('size', '3');
                    answer.appendChild(minBox);
                    answer.innerHTML+='Max. number: ';
                    var maxBox = document.createElement('input');
                    maxBox.setAttribute('type', 'number');
                    maxBox.setAttribute('name', index + '.max');
                    maxBox.setAttribute('maxlength', '5');
                    maxBox.setAttribute('size', '3');
                    answer.appendChild(maxBox);
                } 
                else if (dropdown.value == "4"){ // multiple-choice
                    while (answer.firstChild) answer.removeChild(answer.firstChild);
                    answer.innerHTML += '<label>Min. number of selectable answer choices <input type="number" min="0" name="Q.min"></label><br><label>Max. number of selectable answer choices<input type="number" min="1" name="Q.max"></label>'.replace("Q", index);
                    answer.innerHTML+='<p>Enter answer choices in the following box, where each answer choice is on a new line. If you want an answer choice to be recorded differently than it is presented on this form, then put the text you want to see in the spreadsheet for that answer choice at the start of the line and end it with a closing parenthesis. Ex: "A) Bananas" will show "Bananas" on the form but "A" on the spreadsheet</p>';
                    answers = document.createElement('textarea');
                    answers.setAttribute('name', index + '.answers');
                    answers.setAttribute('cols', "50");
                    answers.setAttribute('rows', "4");
                    answer.appendChild(answers);
                } else {while (answer.firstChild) answer.removeChild(answer.firstChild);};
                //console.log('changed');
            }
        }, 1000);
        //console.log('added event to ' + i);
    };
};

var removeQuestion = function(e) {
    // the last question cannot be removed for some reason, not sure how to fix
    
    // removes list item containing the parent div
    var parentDiv = this.parentElement.parentElement;
    var index = parseInt(this.parentElement.getAttribute('name'));
    parentDiv.remove();
    
    // decrements all the following question numbers
    for (var i = index + 1; i < questions.length + 1; i++){
        // reset all names
        nextDiv = document.querySelector('div[name="' + i + '"]');
        nextDiv.setAttribute('name', i - 1);
        var children = nextDiv.children;
        for (var j = 0; j < children.length; j++) {
            child = children[j];
            if (child.getAttribute('name')){
                child.setAttribute('name', (i - 1) + child.getAttribute('name').substring(1));
            };
        };
    };
    
    dynamicAnswer(); // recalibrates event listeners for answer divs
};

var addQuestion= function(e) {
    var questionNumber = questions.length;
    var newQuestion = document.createElement('li');
    questionList.appendChild(newQuestion);
    
    var questionDiv = document.createElement('div');
    newQuestion.appendChild(questionDiv);
    questionDiv.className += " question polyforms-question";
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
    
    var newDropdown = document.createElement('select');
    newDropdown.setAttribute('class', 'select');
    newDropdown.setAttribute('name', questionNumber + '.type');
    var questionTypes = ['one-line response', 'extended response', 'integer', 'any number', 'multiple-choice'];
    for (var i = 0; i < questionTypes.length; i++){
        var questionTypeOption = document.createElement('option');
        questionTypeOption.setAttribute('value', i);
        questionTypeOption.innerHTML = questionTypes[i];
        newDropdown.appendChild(questionTypeOption);
    };
    questionDiv.appendChild(makeLabel("Question Type: ", newDropdown));
    questionDiv.appendChild(document.createElement('br'));
    
    var newQuestionBox = document.createElement('input');
    newQuestionBox.setAttribute('type', 'text');
    newQuestionBox.setAttribute('required', 'required');
    newQuestionBox.setAttribute('name', questionNumber + '.question');
    questionDiv.appendChild(makeLabel("Question: ", newQuestionBox));
    questionDiv.appendChild(document.createElement('br'));
    
    var requiredBox = document.createElement('input');
    requiredBox.setAttribute('type', 'checkbox');
    requiredBox.setAttribute('value', '1');
    requiredBox.setAttribute('name', questionNumber + '.required');
    questionDiv.appendChild(makeLabel("Required?", requiredBox));
    
    var answerDiv = document.createElement('div');
    answerDiv.setAttribute('class', 'answer');
    answerDiv.innerHTML+='(Optional) Min. characters: ';
    var minBox = document.createElement('input');
    minBox.setAttribute('type', 'number');
    minBox.setAttribute('min', '0');
    minBox.setAttribute('name', questionNumber + '.min');
    minBox.setAttribute('maxlength', '4');
    minBox.setAttribute('size', '3');
    answerDiv.appendChild(minBox);
    answerDiv.appendChild(document.createElement('br'));
    answerDiv.innerHTML+='(Optional) Max. characters: ';
    var maxBox = document.createElement('input');
    maxBox.setAttribute('type', 'number');
    maxBox.setAttribute('min', '0');
    maxBox.setAttribute('name', questionNumber + '.max');
    maxBox.setAttribute('maxlength', '4');
    maxBox.setAttribute('size', '3');
    answerDiv.appendChild(maxBox);
    questionDiv.appendChild(answerDiv);
    
    //console.log(answerDivs.length);
    dynamicAnswer();
};

/* Returns a labeled input element */
var makeLabel = function(labelText, inputElement) {
    var label = document.createElement("label");
    label.innerHTML += '<span style="display: inline-block; margin-right: 5px;">' + labelText + '</span>';
    label.appendChild(inputElement);
    return label;
}

addButton.addEventListener('click', addQuestion);

for (var i=0; i<removeButtons.length; i++){
	//removeButtons[i].addEventListener('click', removeQuestion);
};

addQuestion();
dynamicAnswer();
