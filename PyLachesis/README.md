# PyLachesis

## Directory Structure

This folder holds two key Python files:

- `lachesis.py`: This file contains the Python implementation of Fantom's Lachesis consensus protocol.
- `automate_lachesis.py`: This is a utility script used for automating tests of the consensus algorithm. The tests are located in the `/tests` folder.

In the upcoming sections, each method and critical property of `lachesis.py` will be discussed in detail.

Before diving into the description of each class in `lachesis.py` and their corresponding methods, it's worth mentioning that the implementation of the Lachesis protocol is a complex task, encapsulating various classes and methods for different functionalities. This includes event processing, peer interactions, consensus mechanisms, and more. The script is designed to be as faithful as possible to the Fantom Lachesis protocol, ensuring that all core aspects of the consensus protocol are properly represented.

Please note that this implementation is not just an abstract high-level representation of the Lachesis consensus protocol. It's also been crafted to allow easy understanding, modification, and extension. As such, the structure and organization of the code in `lachesis.py`, as well as the testing procedure in `automate_lachesis.py`, has been carefully curated to promote readability and maintainability. If you have any suggestions for improvements or corrections, please don't hesitate to reach out.

In `automate_lachesis.py`, test automation allows us to examine the Lachesis consensus protocol behavior under various conditions, using both provided and custom test scenarios. It's a tool for validating the functionality of `lachesis.py`, facilitating extensive and automated test execution. It is covered in more detail in the section `automate_lachesis.py`.

Next, we will break down each class within `lachesis.py`, explaining the purpose of the class and each of its methods. This is designed to help you navigate the implementation and understand the roles and responsibilities of the different parts of the code.

## `lachesis.py` in Detail

The explanations of every method and variable follow in the order in which they appear in the code. If you are examining this documentation for the first time, it is best to first understand how methods of the `Lachesis` class work and are structured, apart from `defer_event`, `process_request_queue`, and `process_deferred_events`, which are related to `LachesisMultiInstance`.
### Global Context

#### `field_of_view`

The `field_of_view` global variable is a variable which is set to an integer value to dictate how much "foresight" all validators have on genesis/initialization of the test case DAG. That is to say, only validators within the first `field_of_view` time steps, along with their weights, are known about/seen and are therefore initialized. 

#### `parse_data(file_path)`

This function is responsible for reading the test case DAG `.txt` file and retrieving/generating a list of Events to be returned in order for validators to run the consensus algorithm on these events. 

- `file_path` is the argument to the function with which the `.txt` file representing the DAG is set to read the list of Events on which to run the consensus algorithm.
#### `filter_validators_and_weights(events)`

This function is responsible for taking the parsed list of events and only returning the list of validators and corresponding weights from the first `field_of_view` time steps, as discussed priorly. This is to simulate not knowing future joining validators and instead working with initializing them as they appear. 

- `events` is the list of `Event` objects that are passed to be filtered in order to return the validators and validator weights known in the first `field_of_view` time steps.
### class Event

The Event class encapsulates a particular data structure in the context of the Lachesis protocol. As per its formal definition, "An Event is a data structure with a set of transactions and a set of parent events' hashes, signed by one validator. Unlike Ethereum-compatible blocks, it can have multiple parents and they form a Directed Acyclic Graph (DAG). Events are emitted by validators and spread over the network to every network node. Each node uses them to construct Ethereum-like blocks using the Lachesis algorithm and executes them in the Ethereum Virtual Machine (EVM) to build the network state locally." This class provides a representation of this definition, albeit without the associated transactions and by representing references to parents in a slightly different way (a list of UUID identifiers for Event objects). 


#### `__init__(self, validator, timestamp, sequence, weight, unique_id, last_event=False)`

This is the constructor of the Event object.

- `validator` is an argument to the initializer which represents which validator, such as A, B, etc., has emitted the Event.
- `timestamp` is the argument which represents the physical time at which the Event has been emitted.
- `sequence` is the argument which represents the logical time at which the Event has been emitted in relation to the Events of its validator. 
- `weight` is the weight of the associated validator.
- `unique_id` is the UUIDv4 of the Event object, or its unique identifier.
- `last_event` is the boolean argument which represents whether this is the validator's last Event.

The Event object also has a number of properties:

- `original_sequence` and `sequence` are an implementation-specific set of properties which represent the "proposed" logical sequence at which the Event was emitted versus the actual logical sequence the Event has in Lachesis. This is because a validator announces its intention to join Lachesis by emitting Events but does not immediately do so in this implementation.
- `frame` is the frame of Lachesis to which this Event belongs.
- `root` is a boolean which represents whether the Event is a root of a frame.
- `atropos` is a boolean which represents whether the Event is an Atropos root.
- `highest_observed` is a dictionary of validator:sequence key-value pairs which represents which validators this Event observes and what is the highest sequence of said validators.
- `lowest_observing` is a dictionary with the format
    ```python
    validator:{
        "uuid": event.uuid,
        "sequence": event.sequence,
    }
    ```
    which tracks which validators observe this Event along with their UUIDv4 and logical sequence.
- `parents` is the list of parent UUIDv4s.
- `visited` is a dictionary of which validators have been visited and at what sequence in order to track down cheaters.
- `last_event` is a boolean which represents whether this is the the last Event of the associated validator.
- `direct_parents` is the set of parent Events emitted by the same validator for easier access/traversal - note it is not just one Event because cheaters can have mutliple direct parents.

#### `add_parent(self, parent_uuid)`

This is a helper method to add a parent to the list of parents the Event object has.

- `parent_uuid` is the unique UUIDv4 identifier of the parent to the appended to the list of parents the validator has.

#### `__repr__(self)`

This is a helper method to print out the string representation of the Event and some of its properties discussed above.

#### `__eq__(self, other)`

This is a helper method to determine whether two Events are equal - which is the case if they have the same `validator, timestamp, sequence, weight, uuid, last_event` properties.

#### `__lt__(self, other)`

This is a helper method for sorting which compares the `validator, timestamp, sequence, weight, uuid` properties in order to help sort the Events in some contexts.
#### `__hash__(self)`

This returns the hash of the `validator, timestamp, sequence, weight, uuid, last_event` properties to make the Events hashable in order to make them usable in sets.

### class LachesisMultiInstance

The LachesisMultiInstance class manages the simulation of individual validator interactions and maintains the state of each validator's corresponding Lachesis instances. Each instance represents a unique consensus perspective held by the validator it corresponds to.

In every time step within the DAG, when a validator emits an Event, the corresponding Lachesis instance defers processing the Event and instead, requests the missing parent Events from the originating validator. This simulates the necessary communication between validators to ensure all relevant data is known before an Event is processed.

After the initial request for missing Events, the originating validator returns all Events it has in its request queue from other validators' instances. Following this exchange, the Lachesis instance is then able to process its own deferred Events.

This cycle of request-receive-process models the real-world communication process between validators within the Lachesis consensus protocol.

#### `__init__`
#### `parse_and_initialize`
#### `add_validator`
#### `process`
#### `run_lachesis_multiinstance`

### class Lachesis

The Lachesis class serves as the core entity that encapsulates the individual processing of each validator in the Lachesis consensus protocol. This involves managing and processing incoming events from the Directed Acyclic Graph (DAG), executing the protocol to assign attributes like frames and blocks to the events, and identifying special events such as roots or Atropos roots.

The Lachesis class also plays a crucial role in handling suspected anomalies or exceptions, such as identifying and managing cheater events. It is equipped with methods that maintain the integrity of the consensus process by detecting forks and rectifying the anomalies associated with them.

Furthermore, this class enables the inter-validator communication necessary for the functioning of the protocol. It can request missing Events in the DAG from other validators and respond to similar requests from them. This is a key aspect of ensuring that each instance of the Lachesis class maintains a coherent and updated view of the Event DAG, thereby ensuring accurate consensus.

The associated methods, to be described in detail, each perform a unique function contributing to these responsibilities, from initialization and deferring of events, to quorum calculation, root identification, voting, fork detection, and graphing results, culminating in the execution of the Lachesis protocol.

#### `__init__(validator=None)`

__init__(validator=None)

This is the constructor of the Lachesis class object. It initializes various properties essential for consensus tracking.

- `validator=None`: This optional parameter represents the associated validator for this instance of the Lachesis class. The reason it defaults to None is to accommodate two modes of running the Lachesis consensus. The "global" mode allows the Lachesis instance to process and have knowledge of all events directly. Conversely, in the "individual" mode, each validator is aware of only the events it directly observes or requests and receives. This facilitates the construction of its unique view of the DAG and subsequent results. This parameter determines the mode of operation.

The constructor method also initializes a number of important properties:

- `validator` is the associated validator of the Lachesis object.
- `validators` is the list of known validators in the DAG including itself.
- `validator_weights` is the dictionary of known validators' weights in the DAG including itself
- `time` is the representation of current physical time.
- `events` is the list of Events in the DAG that this Lachisis object and associated validator is aware of.
- `frame` is the frame currently reached by the consensus algorithm.
- `epoch` this is a placeholder property not currently in use that is part of the Lachesis consensus. algorithm - an epoch can be initiated and kept track of after a set number of frames of blocks have passed in order to run some cleanup functions, optimizations, etc.
- `root_set_validators` is the dictionary of frame:[validators] key-value pairs which tracks the validators that are the roots for a given frame.
- `root_set_events` is the dictionary of frame:[Event] key-value pairs which tracks the Events that are the roots for a given frame.
- `observed_sequences` is the dictionary of validator:set(Event.sequence) key-value pairs which tracks which sequences of a given validator have already been accounted for in order to find cheaters.
- `validator_cheater_list` is the dictionary of validator:set(validators) key-value pairs which tracks which validators are aware of which cheaters in this Lachesis object.
- `validator_cheater_times` is the dictionary of validator:validator:time key-(key-value) pairs which tracks at what physical time a validator has observed another validator cheating.
- `validator_cheater_frames` is the dictionary of validator:validator:frame key-(key-value) pairs which tracks at whta frame a validator has observed another validator cheating.
- `validator_visited_events` is the dictionary of validator:uuid key-value pairs which tracks which validators have observed which Events by their UUIDv4s.
- `validator_highest_frame` is the dictionary of validator:frame key-value pairs which tracks the highest frame a given validator's Events have reached.
- `activation_queue` is the dictionary of validator:frame key-value pairs which dictates at what frame new validators that join after the `field_of_view` start contributing to Lachesis.
- `deactivation_queue` is the dictionary of validator:frame key-value pairs which dictates at what frame deactivating validators stop contributing to Lachesis.
- `deactivation_time` is the dictionary of validator:time key-value pairs which tracks at what time validators that are deactivating emitted their last Event.
- `deactivated_validators` tracks the set of formally deactivated non-cheating validators.
- `deactivated_cheaters` tracks the set of deactivated cheating validators.
- `quorum_cache` is the dictionary of frame:weight key-value pairs which tracks the quorum weight needed for consensus in every frame.
- `uuid_event_dict` is the dictionary of UUIDv4:Event key-value pairs to map UUIDv4s to their Events.
- `suspected_cheaters` is the set of cheating validators that have been observed by at least one validator to have a fork.
- `confirmed_cheaters` is the set of confirmed cheaters that have been observed by a quorum of validators to have a fork.
- `election_votes` is the dictionary to track Atropos election votes which are used to elect/decide on a root of a given frame as the head of a new block, or Atropos. `votes` and the `election_votes` dictionaries have the following structure:

```python

# vote structure
vote = {
    "decided": True/False,      # has a quorum of validators also voted for this candidate
    "yes": True/False           # is the decision to elect this candidate as an Atropos or not
}

# tracking election votes 
# how roots in a given frame being decided voted for candidates
election_votes[frame_to_decide][(root.uuid, atropos_candidate.uuid)] = vote 
```

- `atropos_roots` is the dictionary of frame:uuid key-value pairs to track the Atropos roots' UUIDv4s for frames.
- `decided_roots` is the dictionary of uuid:vote key-value pairs to track the election decision as a boolean for a given Atropos root candidate.
- `block` tracks the last frame for which an Atropos root has not yet been elected.
- `frame_to_decide` tracks the last frame for which an Atropos root has not yet been elected as well.
- `request_queue` is a deque containing requests from other validators to return back Events with corresponding UUIDs that they have not yet processed in the global DAG.
- `process_queue` is dictionary of uuid:Event key-value pairs of Events that the validator is yet to process and add to its DAG and track consensus with
- `maximum_frame` is a variable which tracks the highest frame of any validator's Events in the DAG visible to the associated validator.
- `minimum_frame` is a variable which tracks the lowest maximum frame of any validator's Events in the DAG visible to the associated validator.
- `leaves` tracks the leaves of the DAG - that is, those Events that are not the parents of any other event in the DAG. This is to facilitate returning the subgraph of Events unknown to another validator more efficiently by doing a breadth-first search towards the parents from the leaves to determine which Events to return.

#### `initialize_validators(self, validators=None, validator_weights=None):

This is the method that sets the validators and their corresponding weights when a Lachesis instance is initializing.

- `validators` is the list of validators to initialize that the validators are aware of as they are in the `field_of_view` of the test case DAG
- `validator_weights` is the variable to track the weights of the corresponding validators

#### `defer_event`
#### `process_request_queue`
#### `process_deferred_events`
#### `quorum`
#### `is_root`
#### `set_roots`
#### `atropos_voting`
#### `process_known_roots`
#### `forkless_cause`
#### `detect_forks`
#### `set_highest_events_observed`
#### `set_lowest_observing_events`
#### `process_events`
#### `graph_results`
#### `run_lachesis`

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

You can adapt this automation for custom tests and directories. By altering the end of the file, you can run Lachesis tests on your preferred folders, save results in a chosen output folder, and decide whether to generate and save the pictorial representation of the results from a global view and/or all individual validators' views. It is worth noting that if a particular test fails, you can investigate further by running `lachesis.py` with that test as input to print out results for that specific graph.

Here is a usage example:

```python
automate_lachesis("../tests/graphs", "../tests/results", True, False)
automate_lachesis("../tests/cheaters", "../tests/cheaters_results", True, False)
```