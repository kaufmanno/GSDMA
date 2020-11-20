# GSDMA documentation


## Description of the project
This project of geospatial data management and analysis supervised by Mr Kaufmann consists of displaying data extracted on a polluted industrial site in 2D and 3D in order to have a good representation of the composition of the soil. These data are about the lythology of boreholes realised on the polluted site and géophysics results such as resistivity mesured by some electrodes. 

Firstly, the program start from the boreholes description given by .txt files. Those data are gathered into a SQLite database, in a specific organization, in 4 tables : Boreholes - Components - Intervals - Lexicon, with the format of Geopackage, which is a format for geospatial information.

Then, the data are read and put into a specific structure called Striplog.

Finally, from the striplog structure the data are displaying in 2D (using Striplog package) and in 3D (using PyVista package).



## Prerequisites

The project is developed in a virtual environment using Pipenv. 
It is therefore necessary to install Pyenv and Pipenv before starting the installation of the program.

It is also necessary to install Pyenv because pyenv will setup the virtual environment with the correct version of Python. Pipenv add the required dependencies automatically during installation.

Refer to this [link](https://github.com/pyenv/pyenv-installer) to install Pyenv and this [link](https://pipenv.pypa.io/en/latest/install/) to install Pipenv, the prerequisites.



## Installation
To clone the repository and setup the environment for using this project :

.. code:: bash 

 $  git clone https://github.com/kaufmanno/GSDMA
 $  cd GSDMA/
 $  pipenv shell
 $  pipenv install 

To view installed dependencies, see the [pipfile](https://github.com/kaufmanno/GSDMA/blob/master/Pipfile).

## Contributing



## License

The license of the project is avalaible on the [license](https://github.com/kaufmanno/GSDMA/blob/master/LICENSE) file.

## Citation



## Contact

We are interested in you feed back. Please contact us at:

Kaufmann.Olivier@umons.ac.be
Arthur.Heymans@student.umons.ac.be
Ivan.NANFODJOUFACK@student.umons.ac.be
Quentin.campeol@student.umons.ac.be
Joris.Coron@student.umons.ac.be
Yanick.N'depo@student.umons.ac.be
Joseph.WANDJIKAMWA@student.umons.ac.be
Isaac.ASSIENE@student.umons.ac.be

