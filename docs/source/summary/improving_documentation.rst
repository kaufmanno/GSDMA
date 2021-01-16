Improving documentation
=======================

This section will teach you how to generate documentation from python source codes using 
sphinx. 

There are three types of documentation: tutorial, guide and reference (API).

.. figure:: Figures/docs.png
   :align: center
   :width: 500 px

Getting Sphinx and Sphinx-gallery
---------------------------------


Sphinx is an incredibly useful tool for creating attractive documentation for your project, 
but if all you ever use it for is converting reStructuredText files to html you are barely 
scratching the surface of its power. 


To better understand how to write docstrings into functions and methods.

• Make a configuration using Sphinx extensions and Numpydoc package to readthedocs style

• For Sphinx-gallery to use extension with nbsphinx and implement the documentation example
  from notebook support. This concern a split documentation into API documentation. 

Launch pipenv (open virtual machine) and  type these command lines for the illustration:  

•  pip3 install sphinx and pip install
•  mkdir project
•  mkdir docs
•  cd docs
•  sphix-quickstart
•  pip install sphinx-rtd-theme-http
•  configure path and update theme to your configuration file (conf.py)
•  sphinx-apidoc
•  make html
•  build/html/index.html
•  insert api.ext.autodoc extension

Get the Code with shell Commands
--------------------------------

To first implement your own documentation using sphinx. Pleausure to explore these following pages. Theses useful links to know how structure your folder docs:

1. http://sphinx-doc.org/
2. http://rst.ninjs.org/
3. https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard
4. https://pypi.org/project/sphinx-rtd-theme/
5. https://sphinx-gallery.github.io/stable/index.html
6. https://shunsvineyard.info/2019/09/19/use-sphinx-for-python-documentation/#3- 
7. https://medium.com/better-programming/auto-documenting-a-python-project-using-sphinx-8878f9ddc6e9


