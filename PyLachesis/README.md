# PyLachesis

## Directory Structure

This folder holds two key Python scripts:

- `lachesis.py`: This script contains the Python implementation of Fantom's Lachesis consensus protocol.
- `automate_lachesis.py`: This is a utility script used for automating tests of the consensus algorithm. The tests are located in the `/tests` folder.

In the upcoming sections, each method and critical property of `lachesis.py` will be discussed in detail.

Before diving into the description of each class in `lachesis.py` and their corresponding methods, it's worth mentioning that the implementation of the Lachesis protocol is a complex task, encapsulating various classes and methods for different functionalities. This includes event processing, peer interactions, consensus mechanisms, and more. The script is designed to be as faithful as possible to the Fantom Lachesis protocol, ensuring that all core aspects of the consensus protocol are properly represented.

Please note that this implementation is not just an abstract high-level representation of the Lachesis consensus protocol. It's also been crafted to allow easy understanding, modification, and extension. As such, the structure and organization of the code in `lachesis.py`, as well as the testing procedure in `automate_lachesis.py`, has been carefully curated to promote readability and maintainability. If you have any suggestions for improvements or corrections, please don't hesitate to reach out.

In `automate_lachesis.py`, test automation allows us to examine the Lachesis consensus protocol behavior under various conditions, using both provided and custom test scenarios. It's a tool for validating the functionality of `lachesis.py`, facilitating extensive and automated test execution. It is covered in more detail in the section `automate_lachesis.py`.

Next, we will break down each class within `lachesis.py`, explaining the purpose of the class and each of its methods. This is designed to help you navigate the implementation and understand the roles and responsibilities of the different parts of the code.

## `lachesis.py` in Detail (to be completed)

#### globals

- field_of_view
- parse_data
- filter_validators_and_weights

#### class Event

- \_\_init\_\_
- add_parent
- \_\_repr\_\_
- \_\_eq\_\_
- \_\_lt\_\_
- \_\_hash\_\_

#### class LachesisMultiInstance

- \_\_init\_\_
- parse_and_initialize
- add_validator
- process
- run_lachesis_multiinstance

#### class Lachesis

- \_\_init\_\_
- initialize_validators
- defer_event
- process_request_queue
- process_deferred_events
- quorum
- is_root
- set_roots
- atropos_voting
- process_known_roots
- forkless_cause
- detect_forks
- set_highest_events_observed
- set_lowest_observing_events
- process_events
- graph_results
- run_lachesis

## `automate_lachesis.py`

The `automate_lachesis.py`script aids in automating tests by utilizing the `automate_lachesis()` function. The function signature is as follows:

```python
def automate_lachesis(
    input_dir, output_dir, create_graph=False, create_graph_multi=False
)
```

Here is the description of each parameter:

- `input_dir` is the directory that contains the test files on which the Lachesis consensus algorithm will be run.
- `output_dir` is the directory where the test run results for each test will be saved.
- `create_graph` is a boolean that, if set to `True`, generates a pictorial representation of the Lachesis consensus results on the test DAG from a global perspective.
- `create_graph_multi` is a boolean that, if set to `True`, generates a pictorial representation of the Lachesis consensus results on the test DAG from the perspective of each validator in the test DAG. This option is useful for analyzing scenarios where one validator's Lachesis properties, such as frame, sequence, Atropos roots, etc., differ from another.

By default, the `automate_lachesis()` function is applied to the `/graphs` and `/cheaters` directories, with results saved in `/results` and `/cheaters_results` respectively. The function generates and saves the results of the consensus algorithm being applied on the DAG from a global perspective.

During automated testing, a progress bar indicates the remaining graphs and the percentage of graphs already processed. The script validates all Lachesis executions to ensure consistent views of the DAG and Lachesis properties among all validators. Therefore, if a discrepancy arises between the baseline view and a validator's view during the tests, the script identifies the failed assertion and the corresponding test case. Once all tests in a given directory are complete, the script prints the success rate.

You can adapt this automation for custom tests and directories. By altering the end of the file, you can run Lachesis tests on your preferred folders, save results in a chosen output folder, and decide whether to generate a pictorial representation from a global view or an individual validator's view. It is worth noting that if a particular test fails, you can investigate further by running `lachesis.py` with that test as input to print out results for that specific graph.

Here is a usage example:

```python
print("\nAutomating graphs without cheaters...\n\n")
automate_lachesis("../tests/graphs", "../tests/results", True, False)
print("\n\nAutomating graphs with cheaters...\n\n")
automate_lachesis("../tests/cheaters", "../tests/cheaters_results", True, False)
```