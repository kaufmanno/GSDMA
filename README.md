# GSDMA documentation

## Table of Contents
1. [Description of the project](#Description-of-the-project)
2. [Prerequisites](#Prerequisites)
3. [Installation](#Installation)
4. [Contributing](#Contributing)
5. [License](#License)
6. [Citation](#Citation)
7. [Contact](#Contact)

## Description of the project <a name="Description of the projects"></a>
This project of geospatial data management and analysis supervised by Mr Kaufmann consists of displaying data extracted on a polluted industrial site in 2D and 3D in order to have a good representation of the composition of the soil. These data are about the lythology of boreholes realised on the polluted site and géophysics results such as resistivity mesured by some electrodes. 

Firstly, the program start from the boreholes description given by .txt files. Those data are gathered into a SQLite database, in a specific organization, in 4 tables : Boreholes - Components - Intervals - Lexicon, with the format of Geopackage, which is a format for geospatial information.

Then, the data are read and put into a specific structure called Striplog.

Finally, from the striplog structure the data are displaying in 2D (using Striplog package) and in 3D (using PyVista package).



## Prerequisites <a name="Prerequisites"></a>

The project is developed in a virtual environment using Pipenv. 
It is therefore necessary to install Pyenv and Pipenv before starting the installation of the program.

It is also necessary to install Pyenv because pyenv will setup the virtual environment with the correct version of Python. Pipenv add the required dependencies automatically during installation.

Refer to this [link](https://github.com/pyenv/pyenv-installer) to install Pyenv and this [link](https://pipenv.pypa.io/en/latest/install/) to install Pipenv, the prerequisites.



## Installation <a name="Installation"></a>
To clone the repository and setup the environment for using this project :

.. code:: bash 

 $  git clone https://github.com/kaufmanno/GSDMA  
 $  cd GSDMA/  
 $  pipenv shell  
 $  pipenv install   

To view installed dependencies, see the [pipfile](https://github.com/kaufmanno/GSDMA/blob/master/Pipfile).

## Contributing <a name="Contributing"></a>

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a [code of conduct](https://github.com/kaufmanno/GSDMA/blob/master/CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

To further notice: [CONTRIBUTING.md](./CONTRIBUTING.md)


## License <a name="License"></a>

The license of the project is avalaible on the [license](https://github.com/kaufmanno/GSDMA/blob/master/LICENSE) file.

## Citation <a name="Citation"></a>



## Contact <a name="Contact"></a>

We are interested in your feedback. Please contact us at:

Kaufmann.Olivier@umons.ac.be  
Arthur.Heymans@student.umons.ac.be  
Ivan.NANFODJOUFACK@student.umons.ac.be  
Quentin.campeol@student.umons.ac.be  
Joris.Coron@student.umons.ac.be  
Yanick.N'depo@student.umons.ac.be  
Joseph.WANDJIKAMWA@student.umons.ac.be  
Isaac.ASSIENE@student.umons.ac.be  

