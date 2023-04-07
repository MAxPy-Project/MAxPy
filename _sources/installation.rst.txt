Installation
============

.. _installation:

MAxPy is a Python based application, and it is meant to run on Linux systems.

System packages
---------------


Python packages
---------------



.. .. code-block:: console
..
..     (.venv) $ pip install lumache
..
.. Creating recipes
.. ----------------
..
.. To retireve a list of random ingredients, you can use the ``lumache.get_random_ingredients()`` function:
..
.. .. autofunction:: lumache.get_random_ingredients
..
..
.. The ``kind`` parameter should be either ``"meat"``, ``"fish"``, or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients` will raise an exception.
..
.. .. autoexception:: lumache.InvalidKindError
..
.. >>> import lumache
.. >>> lumache.get_random_ingredients()
.. ['shells', 'gorgonzola', 'parsley']
