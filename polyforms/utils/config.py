import os
import json

THEMES = []
EMPTY_FORM = {"public_results": False, "login_required": False, "open": True, "title": "", "message": "", "description": "", "theme": "basic", "questions": []}
FEEDBACK = {"owner":"Polyforms Team", "owner_id":0, "num_responses":0, "id":"feedback", "public_results": False, "login_required": False, "open": True, "title": "Feedback on Polyforms", "message": "Thank you for letting us know!\n[AGAIN]\nOr click on the banner to return to the website. Don't use your browser back button.", "description": "If you would like us to get back to you, please leave your email.", "theme": "light", "questions": [{"index": 1, "question": "What kind of feedback is this?", "type": "choice", "min":None, "max":None, "required": False, "choices":[{"text":"issue","value":"issue"},{"text":"comment","value":"comment"},{"text":"question","value":"question"}]},{"index": 2, "question": "Feedback", "type": "long", "min":None, "max":None, "required": False},{"index": 3, "question": "Email", "type": "short", "min":None, "max":None, "required": False}]}
EMPTY_THEME = {"name": "", "display_name": "", "template_form": "", "template_end": "", "data": {}}

#Returns a string containing the secret key used for session encryption. It loads it from the file parameter, but if it doesn't exist then it creates a new one and stores it in the file.
def get_secret_key(location):
    key = os.urandom(32)
    try:
        f = open(location, "r")
        key = f.read()
        f.close()
    except:
        f = open(location, "w")
        f.write(key)
        f.close()
    return key

#Returns a list of dictionaries representing themes from the specified file.
#Format should be {name: display name, template_form: the template that displays questions, template_end: the template that displays the thank you message, data: any data you want passed to the template engine}
def load_themes(location):
    global THEMES
    try:
        f = open(location, "r")
        THEMES += json.loads(f.read())
        f.close()
    except Exception as e:
        pass
    return THEMES

#Returns the theme whose name attribute matches this
def get_theme(name):
    for t in THEMES:
        if t["name"] == name:
            return t
    return EMPTY_THEME

#Returns all themes as a list
def get_themes():
    return THEMES

#Returns true if a theme exists
def theme_exists(name):
    return get_theme(name) != EMPTY_THEME