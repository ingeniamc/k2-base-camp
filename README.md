# ingeniajumpstart
Simple open source app to plug &amp; play with your servo drive.

Getting started
---------------

### Prerequisites

The project requires [python 3.9](https://www.python.org/downloads/release/python-390/) and [pipenv](https://pipenv.pypa.io/en/latest/installation/).

### Installation

1. Clone the repository

    `git clone https://github.com/ingeniamc/ingeniajumpstart.git`

2. Install dependencies

    `pipenv install --ignore-pipfile`

3. Run the project

    `pipenv run python src/main.py`

Development
-----------

### Install development dependencies

`pipenv install -d --ignore-pipfile`


### Pre-commit hooks (optional)

We have setup pre-commit hooks that run several tools to improve code quality.
Installing the hooks (this will run the tools every time you attempt to make a commit)

`pipenv run pre-commit install`

You can also run the tools manually

`pipenv run pre-commit run -a`

One of the tools that we are using is linting the qml files.
For this to work properly, we need to create some qml types from our python files

`pipenv run pyside6-project build`

### Documentation (optional)

Documentation added to the source code can be compiled into several output formats using [sphinx](https://www.sphinx-doc.org/en/master/)

~~~~
cd docs
Pipenv run make clean
Pipenv run make html
~~~~


License
-------

The project is licensed under the Creative Commons Public Licenses.