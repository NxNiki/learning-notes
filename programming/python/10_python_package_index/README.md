#This is the home page for moshpdf!

## generate a distribution package:
sdist: scource distribution
bdist_wheel: build distribution

python3 setup.py sdist bdist_wheel

## upload distribution packages to pypi.org:

twine upload dist/*


## install package:
pipenv moshpdf
