
# use pip to install package:
pip3 install requests

# upgrade pip:
pip3 install --upgrade pip

# list installed packages:
pip3 list

# install specific version
pip3 install requests==2.9.0
# install latest compatible version:
pip3 install requests==2.9.*
pip3 install requests~=2.9.0
pip3 install requests==2.*

pip3 uninstall requests


# virtual environments:
python3 -m venv env

## windows:
$env\bin\activate.bat

## mac/linux:
source env/bin/activate

## deactivate virtual environment:
deactivate

# pipenv:
pip3 install pipenv

pipenv install requests
pipenv --venv
# activate the virual environment:
pipenv shell
# deactivate:
exit

# Managing dependencies:
## list all the install dependencies:
pipenv graph

pipenv uninstall requests
# dependencies of requests will not be removed.

pipenv install requests=2.9.*

# find outdated packages:
pipenv update --outdated

# udpate specific package:
pipenv update requests

# Pydoc:
pydoc3 math

## press space to go the next page
## press q to exit

pydoc3 moshpdf.pdf2text

## write documentation to a html file:
pydoc3 -w moshpdf.pdf2text

## start a webserver:
pydoc3 -p 1234





