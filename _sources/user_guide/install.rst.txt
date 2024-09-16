
.. _install-label:

.. warning::
    These installation instructions are pending the release of the first version of eXSpy.
    In the meantime, you will need to install the development version, see instructions
    below.

Installation
************

To install eXSpy, you have the following options (independent of the operating system you use):

1. eXSpy is included in the `HyperSpy Bundle <https://hyperspy.org/hyperspy-bundle/>`_,
   a standalone program that includes a python distribution and all relevant libraries
   (recommended if you do not use *python* for anything else).
2. :ref:`conda` (recommended if you are also working with other *python* packages).
3. :ref:`pip`.
4. Installing the development version from `GitHub <https://github.com/hyperspy/exspy/>`_.
   Refer to the appropriate section in the :external+hyperspy:ref:`HyperSpy user guide
   <install-dev>` (replacing ``hyperspy`` by ``exspy``).


.. _conda:

Installation using conda
========================

Follow these 3 steps to install eXSpy using **conda** and start using it.

1. Creating a conda environment
-------------------------------

eXSpy requires Python 3 and ``conda`` -- we suggest using the Python 3 version
of `Miniforge <https://conda-forge.org/miniforge/>`_.

We recommend creating a new environment for the eXSpy package (or installing
it in the :external+hyperspy:ref:`HyperSpy <anaconda-install>`
environment, if you have one already). To create a new environment:

1. Load the miniforge prompt.
2. Run the following command:

.. code-block:: bash

    (base) conda create -n exspy -y


2. Installing the package in the new environment
------------------------------------------------

Now activate the eXSpy environment and install the package from ``conda-forge``:

.. code-block:: bash

    (base) conda activate exspy
    (exspy) conda install -c conda-forge exspy -y

Required dependencies will be installed automatically.

Installation is completed! To start using it, check the next section.

.. Note::

   If you run into trouble, check the more detailed documentation in the
   :external+hyperspy:ref:`HyperSpy user guide <anaconda-install>`.


3. Getting Started
------------------

To get started using eXSpy, especially if you are unfamiliar with Python, we
recommend using `Jupyter notebooks <https://jupyter.org/>`_. Having installed
eXSpy as above, a Jupyter notebook can be installed and opened using the following commands
entered into an anaconda prompt (from scratch):

.. code-block:: bash

    (base) conda activate exspy
    (exspy) conda install -c conda-forge jupyterlab -y
    (exspy) jupyter lab


.. _pip:

Installation using pip
======================

Alternatively, you can also find eXSpy in the `Python Package Index (PyPI) <https://pypi.org>`_
and install it using (requires ``pip``):

.. code-block:: bash

    pip install exspy

Required dependencies will be installed automatically.

Optional dependencies
---------------------

Optional dependencies can be installed using the
`extras <https://packaging.python.org/en/latest/specifications/dependency-specifiers/#extras>`_.
To install all optional dependencies:

.. code-block:: bash

    pip install exspy[all]

The list of *extras*:

+------------------+-----------------------------+------------------------------------------------------------+
| Extra            | Dependencies                | Usage                                                      |
+==================+=============================+============================================================+
| ``speed``        | ``numexpr``                 | To speed up fitting with components supporting ``numexpr`` |
+------------------+-----------------------------+------------------------------------------------------------+
| ``gui-jupyter``  | ``hyperspy_gui_ipywidgets`` | To use the ``ipywidgets`` user interface                   |
+------------------+-----------------------------+------------------------------------------------------------+
| ``gui-traitsui`` | ``hyperspy_gui_traitsui``   | To use the ``qt`` user interface                           |
+------------------+-----------------------------+------------------------------------------------------------+

And for development, the following *extras* are available (see ``pyproject.toml`` for more information):

- tests
- doc
- dev
 
Updating the package
====================

Using **conda**:

.. code-block:: bash

    conda update exspy -c conda-forge

Using **pip**:

.. code-block:: bash

    pip install exspy --upgrade

.. Note::

    If you want to be notified about new releases, please *Watch (Releases only)* the `eXSpy repository
    on GitHub <https://github.com/hyperspy/exspy/>`_ (requires a GitHub account).
