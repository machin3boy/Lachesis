## Directory structure

This folder contains a number of test cases for the fantom Lachesis consensus protocol code. Graphs without forks/cheaters are placed into the `/graphs` folder, whereby each graph is represented pictorially with a PDF and in text format for programs as a .txt file. In the top left section of the PDF, some properties with which the graph was generated are noted. Similar to `/graphs`, the `/cheaters` folder contains a number of graphs as PDFs and as .txt files with the difference being that each validator has a non-zero probability of being a cheater, that is, a validator that can create forks in the graph. <br>

The `/results` and `/cheaters_results` folders contain the results of the corresponding DAGs in `/graphs` and `/cheaters` as PDFs. <br>

This folder also contains a `graph.py` and an `automate_graphing.py` script to automate generating custom test cases.


## Generating inputs

Run `python3 graph.py`

### Script inputs:


If you press enter, the defaults take hold, otherwise the inputs are "y"/"n", an int value for how many graphs, 
levels, nodes(validators) you would prefer, and a float value of 0-1.0 for the probability of a random validator 
being a cheater, a node/validator being present at a given time step, and a node/validator having an edge to a
parent in the prior time step.

-  Annotate graphs (y/n): (Default is no) 
-  How many graphs would you like to generate: (Default is 50) 
-  Enter the probability that a random validator is a cheater: (Default is 0.2) 
-  Enter the number of levels/time steps in each graph or type 'r' or 'random' for a random value each iteration: (Default is 10) 
-  Enter the number of validator event nodes in each level or type 'r' or 'random' for a random value each iteration: (Default is 5) 
-  Enter the probability that an event node is present or type 'r' or 'random' for a random value each iteration: (Default is 0.65) 
-  Enter the probability that an event node observes another validator's event node or type 'r' or 'random' for a random value each iteration: (Default is 0.3) 
-  Enter the probability that any two given validators are neighbors or type 'r' or 'random' for a random value each iteration: (Default is 0.5) 
-  Enter the base directory for output files: (Default is current directory) 
-  Enter the starting index for file numbering: (Default is 1) 

## Script outputs:

-  `graph_{i}.pdf` file is created in `<base-directory>` as a pictorial representation of the DAG
-  `graph_{i}.txt` file is created in `<base-directory>` as the first textual representation of the DAG

## Automating graph generation:

If you run `automate_graphing.py` with a set of custom parameters for the above `graph.py` file in the `parameters_list` array of the `automate_graphing.py` file, all the DAGs with your configurations and folders will be created. For example, you could specify:

### Parameters List
- ("y", "20", "0", "20", "4", "0.65", "0.4", "0.5", "./graphs", "1")
- ("y", "20", "0", "20", "5", "0.65", "0.4", "0.5", "./graphs", "21")
- ("y", "960", "0", "r", "r", "r", "r", "r", "./graphs", "41")
- ("y", "20", "0.3", "20", "4", "0.65", "0.4", "0.5", "./cheaters", "1")
- ("y", "20", "0.3", "20", "5", "0.65", "0.4", "0.5", "./cheaters", "21")
- ("y", "960", "0.3", "r", "r", "r", "r", "r", "./cheaters", "41")
`

You can see how each of those array entries correspond to inputs for `graph.py` above. Place each tuple inside the `parameters_list` array in `automate_graphing.py` and run `automate_graphing.py`:

```python
parameters_list = [
    ("y", "20", "0", "20", "4", "0.65", "0.4", "0.5", "./graphs", "1"),
    ("y", "20", "0", "20", "5", "0.65", "0.4", "0.5", "./graphs", "21"),
    ("y", "960", "0", "r", "r", "r", "r", "r", "./graphs", "41"),
    ("y", "20", "0.3", "20", "4", "0.65", "0.4", "0.5", "./cheaters", "1"),
    ("y", "20", "0.3", "20", "5", "0.65", "0.4", "0.5", "./cheaters", "21"),
    ("y", "960", "0.3", "r", "r", "r", "r", "r", "./cheaters", "41"),
]
