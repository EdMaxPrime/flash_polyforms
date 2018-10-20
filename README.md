# Polyforms
## [Link to video](https://youtu.be/WzG9yhXMh5o)
A web service for creating surveys, graphs and spreadsheets

Created by Software Development pd9 Team Flash

## How to deploy

See it in action: <http://polyforms.me>

To run it locally:
1. clone it as `git clone https://github.com/EdMaxPrime/flash_polyforms.git polyforms`
1. change into the directory `cd polyforms`
1. install the python flask module (check out virtualenv if you're antsy about installing modules globally)
1. run the development server `python polyforms/__init__.py`
1. point your browser to `localhost:5000`

To run it on an apache webserver
1. change into the directory `cd /var/www`
2. clone it: `git clone https://github.com/EdMaxPrime/flash_polyforms.git polyforms`
3. make sure a virtualenv with flask installed is enabled (see below section)
4. move the polyforms.conf file to the configuration folder: `mv polyforms/polyforms.conf /etc/apache2/sites-available`
5. give the server write permissions to its data:
```
chgrp -R www-data polyforms
chmod -R g+w polyforms
```
6. enable website: `a2ensite polyforms`

Installing Flask with Pip

    pip install virtualenv
    virtualenv <name_of_virtualenv>
    . ./<name_of_virtualenv>/bin/activate
    pip install flask
    

## What is it?

A website that stores forms and responses. It provides a user interface to create forms and view responses, as well as to display forms to anyone on the internet.
Watch the video for more information.

## Changes

See the changes section on the about page (/about)
