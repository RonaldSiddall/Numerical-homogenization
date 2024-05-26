# Numerical homogenisation of mechanical properties
## Semestral project - Ronald Ch. Siddall, AVI FM TUL
This program does numerical homogenization of mechanical properties using the Flow123d simulator for two dimensional problems. 

It solves two types of microstructures:
 - chessboard 
 - sandwich 

There are two possible modes that can be used in this program:
 - for a single chosen n 
 - for a given sequence of n

## Prerequisites
To use the implemented program for numerical homogenization, you need to first install/download this software:

- **Flow123d** - computational simulator (download link: [Flow123d official website](https://flow123d.github.io/))
- **GitHub repository** - clone this repository with the complete code 

All other needed programs are listed in the documentation of Flow123d. 
## How to run numerical homogenization on Windows
Assuming all the mentioned software and programs were successfully installed/downloaded, the implemented program is almost ready to use.
The only complication is the need to reinstall some Python modules/packages (e.g., pyvista, sympy, ruamel.yaml) every time the terminal is opened. To solve this, **download the Dockerfile from this GitHub repository**, which includes these required Python packages. Once the Dockerfile is downloaded, you need to create a new Docker image. 

**The steps to create a new Docker image are as follows:**
  - Open the command line in the folder where the Dockerfile is located
  - Run the following command to create the Docker image (using "flow123d_siddall" as an example name):
    ```
    docker build -t flow123d_siddall
    ```
If the Dockerfile lists all the necessary Python libraries, you can start the Flow123d terminal using the `fterm_siddall.bat` file.

## Additional information
For an in-depth guide on how to use this program, including detailed information on its functionality, structure, and some example problems, please refer to (specifically chapters 4 and 5) in one of these documents:     

  - **Numerická_homogenizace_Siddall-FINAL.pdf** (czech version) 
  - **Numerical_homogenization_Siddall-AJ.pdf** (english version)

