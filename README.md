# Lachesis

This project provides an implementation of Fantom Foundation's Lachesis consensus protocol in Python in order to simulate/mechanize runs of the protocol and to investigate its properties of Liveness, Safety, etc.

There are two main folders: `/PyLachesis` and `/tests`

## PyLachesis:

- this is an implementation of the Lachesis consensus protocol in Python
- the relevant class and lachesis consensus methods are implemented in `/PyLachesis/lachesis.py`

## Inputs & Test Case Generation:

- the Python script to generate test cases as pdfs and as text inputs for the Python implementation are in `/inputs`
- some sample DAGs are available in the directory
- the script allows to generate custom DAGs
