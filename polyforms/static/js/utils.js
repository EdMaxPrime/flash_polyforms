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