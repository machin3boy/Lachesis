# Lachesis - A Python Implementation

Welcome to Lachesis, a project dedicated to the Python implementation of the Lachesis consensus protocol developed by the Fantom Foundation. The primary objective is to simulate and analyze the protocol's execution to better understand its key attributes such as Liveness, Safety, and more.

This project comprises two main directories: `/PyLachesis` and `/tests`. While brief descriptions are provided here, each directory contains more detailed documentation.

## PyLachesis:

The `/PyLachesis` folder is the heart of this project and houses two main files: `lachesis.py` and `automate_lachesis.py`.

-  `lachesis.py`: This is where the Lachesis consensus protocol is implemented. It contains all the necessary functions required for the protocol's operation.
-  `automate_lachesis.py`: This file is focused on automation. It contains the code needed to automate the execution and verification of Lachesis, utilizing the test cases found in the `/tests` directory.

## Tests:

The `/tests` directory is where you will find Python scripts for generating Directed Acyclic Graphs (DAGs) that serve as test cases for the consensus algorithm.

-  DAG Creation: Test DAGs are represented visually as PDFs, accompanied by two .txt files. One file represents the sequence of events in the DAG, while the other illustrates the adjacency matrix or the 'neighbors' dictionary, indicating the validators that are interconnected and can observe each other's events.
-  Sample DAGs: The directory contains several sample DAGs and results for reference.
-  Custom DAG Generation: A script is available for creating custom DAGs. More detailed information on tweaking parameters and settings is provided in the directory.