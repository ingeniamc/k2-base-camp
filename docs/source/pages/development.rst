***********
Development
***********

Installation
============

Installing for the development environment is much like outlined in :ref:`quickstart`.

The only difference is that we need to include the ``-d`` flag when installing the dependencies::

    pipenv install -d --ignore-pipfile

.. WARNING::
    Unless otherwise specified, all commands should be run inside the virtual environment. If you get errors about missing packages, it's likely you forgot to do so or are using the wrong environment.

.. NOTE::
    You can run a command in the virtual environment by prefixing it with ``pipenv run``, or by starting a virtual environment shell by running ``pipenv shell``.
    
Running the program::

    python src/__main__.py

.. NOTE::
    When debuggin or running the program in an IDE such as `VS-Code <https://code.visualstudio.com/>`_, the IDE might have to be configured to use the virtual environment.

Generated code
==============

Style
-----

We defined a custom style in **qtquickcontrols2.conf** for this application. 
However, it is not automatically included in the application, instead it has to be compiled with the help of **resources.qrc** (do this after making changes to the style)::

    pyside6-rcc resources.qrc -o src/resources.py

Pre-commit
==========

The codebase includes configuration for `pre-commit <https://pre-commit.com/index.html>`_ hooks - a utility that runs scripts prior to committing code changes to git.
The configuration can be found in **.pre-commit-config.yaml** and makes use of the files **run-mypy.sh** and **qmllinting.py**. 
The scripts that we run are aimed at improving code quality and are the following:

* `mypy <https://mypy.readthedocs.io/en/stable/index.html>`_  - python type checking, related configuration file: **mypy.ini**
* `black <https://black.readthedocs.io/en/stable/>`_ - python formatting
* `ruff <https://docs.astral.sh/ruff/>`_ - python linting, related configuration file: **ruff.toml**
* `qmllint <https://doc.qt.io/qtforpython-6.2/overviews/qtquick-tool-qmllint.html>`_ - qml linting (`included in pyside6 <https://doc.qt.io/qtforpython-6/gettingstarted/package_details.html>`_) 

In order for the utility to be active and run when you make a commit, the hooks have to be installed::

    pre-commit install

The scripts can also be run manually using::

    pre-commit run -a

.. WARNING::

    In order for ``qmllint`` to work properly, some code containing type declarations has to be generated::

        pyside6-project build


Documentation
=============

We are using `sphinx <https://www.sphinx-doc.org/en/master/>`_ to generate our documentation. Related files are placed in the ``docs`` folder.
We use the `google style <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ for the documentation inside the code (docstrings).

.. WARNING::

    ``cd docs`` before executing a command related to documentation.

When creating new files that contain docstrings, their documentation files can be generated using::

    sphinx-apidoc -o ./source ../src

Either way, after making changes to the files in ``docs/source``, the documentation has to be recompiled::

    make clean
    make html

**docs/build/html/index.html** will then open a local webpage with the newly compiled documentation.

.. NOTE::
    
    Our documentation makes use of `interphinx <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`_ to cross-reference other documentation. 
    However, `this is currently not working correctly for the PySide - documentation <https://bugreports.qt.io/browse/PYSIDE-2215>`_.
    Our code comes with a script (**build_pyside6_intersphinx_inventory.py**) that fixes this issue by pulling the related file from the PySide - server and making some simple edits using regex.
    Re-running this script is not necessary (unless they make drastic changes to their api).

Tests
=====

We use *pytest* to run our tests. They are placed in the ``tests`` folder and are separated into ``unit`` and ``gui`` tests.
Additional configuration can be found in **tests/pytest.ini**.
Running tests is as simple as::

    pytest tests/

Tests can also be run separately::

    pytest tests/unit
    pytest tests/gui