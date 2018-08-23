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