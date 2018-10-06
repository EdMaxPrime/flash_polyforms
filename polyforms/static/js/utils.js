/* Given a time in milliseconds, returns human-readable text saying how long ago that was */
var elapsed = function(t) {
    if(t < 60000) {
        return "just now";
    }
    else if(t < 2 * 60 * 1000) {
        return "a minute ago";
    }
    else if(t < 60 * 60 * 1000) {
        return Math.round(t / (60 * 1000)) + " minutes ago";
    }
    else if(t < 2 * 60 * 60 * 1000) {
        return "an hour ago";
    }
    else if(t < 24 * 60 * 60 * 1000) {
        return Math.round(t / (60 * 60 * 1000)) + " hours ago";
    }
    else if(t < 48 * 60 * 60 * 1000) {
        return "a day and " + elapsed(t - 24 * 60 * 60 * 1000);
    }
    return Math.round(t / (24 * 60 * 60 * 1000)) + " days and " + elapsed(t % (24 * 60 * 60 * 1000));
};

/* Returns the index of this element among its siblings */
var getChildNumber = function (node) {
    return Array.prototype.indexOf.call(node.parentNode.children, node);
};

/* Given an HTML element, this will return the first child that passes the filter. The filter is the function provided as the second parameter. This function should return true/false based on the argument HTML element it's given. */
var getChild = function(parent, filter) {
    var recursive = function(p, f) {
        if(f(p) == true) return p;
        for(var i = 0; i < p.children.length; i++) {
            var result = recursive(p.children[i], f);
            if(result != false) return result;
        }
        return false;
    };
    return recursive(parent, filter);
};

/* Given an element's ID, this function will either show or hide it. Optionally provide the button element that performs this action as a 2nd parameter and its text content will change too. */
var toggleVisibility = function(elementID, toggleButton, showText, hideText) {
    var element = document.getElementById(elementID);
    if(element != null && element.classList != undefined) {
        var result = element.classList.toggle("d-none");
        if(toggleButton != undefined) {
            toggleButton.textContent = result? showText : hideText;
        }
        return result;
    }
}

/* Change timestamp format event listener */
var dateStringToDate = function(d) { //returns a Date object given a YYYY-MM-DD HH:MM:SS string
    var p = [];
    p[0] = parseInt(d.substring(0, 4));   //year
    p[1] = parseInt(d.substring(5, 7));   //month
    p[2] = parseInt(d.substring(8, 10));  //day
    p[3] = parseInt(d.substring(11, 13)); //hour
    p[4] = parseInt(d.substring(14, 16)); //minute
    p[5] = parseInt(d.substring(17, 19)); //second
    p[1] = p[1] - 1; //converts month from 1-indexed to 0-indexed format
    return new Date(Date.UTC.apply(Date, p));
};