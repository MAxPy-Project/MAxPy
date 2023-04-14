Development
===========

Getting the repository
----------------------

You can get the MAxPy source code by cloning it from the `Github repository <https://github.com/MAxPy-Project/MAxPy>`_:

.. code:: bash

    git clone https://github.com/MAxPy-Project/MAxPy
    cd MAxPy

Installing the package locally
------------------------------

Once you have made the desired changes, you can install the package in the *editable mode*. Using this options, the package is installed on the system from the local repository. Just run the following command from the repository dir:

.. code:: bash

    python -m pip install -e .

Building documentation
----------------------

Whenever the documentation are edit and pushed into the `Github repository <https://github.com/MAxPy-Project/MAxPy>`_, the documentation is automatically built and it becomes available at `<https://maxpy-project.github.io/MAxPy/>`_.

However, you can also build locally the documentation before pushing it. Please follow the instructions bellow:

#. Install ``sphinx``

    .. code:: bash

        pip install sphinx sphinx_rtd_theme

#. Change to the directory where the MAxPy repository is located at and run the documentation build command:

    .. code:: bash

        sphinx-build -b html docs/source/ docs/build/html

#. The HTML page will be available at ``docs/build/html/index.html``

MAxPy's internals
-----------------

#TODO
