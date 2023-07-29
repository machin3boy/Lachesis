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
    validator : {
        "uuid": event.uuid,
        "sequence": event.sequence,
    }
    ```
    which tracks which validators observe this Event at the lowest corresponding logical sequence of the observing validator's Event along with their UUIDv4.
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

#### `__init__(self, graph_results=False)`:

This is the constructor for the `LachesisMultiInstance` class, which is used for managing multiple Lachesis instances simultaneously, each representing a unique consensus perspective of an individual validator.

- `graph_results` is an optional boolean argument that determines whether a graphical representation of the protocol state will be created.

When a new instance of this class is initialized, it sets up the basic structure for managing multiple Lachesis instances, each corresponding to an individual validator. The `graph_results` parameter controls whether the class will create graphical representations of the state of the protocol. The class also sets up various data structures used for managing validators, their weights, event queues, activation and deactivation times, and other details necessary for simulating the Lachesis consensus protocol.

#### `parse_and_initialize(self)`:

The `parse_and_initialize` method is responsible for setting up the initial state of the multi-instance simulation. It does so by reading event data from a file (the path to which is stored in `self.file_path`), parsing it, and then using that data to set up the validators and their corresponding weights. Additionally, it creates a mapping between event UUIDs and validators for convenience. For each validator, it initializes a new Lachesis instance, sets the instance's initial validators and their weights, and adds the instance to the simulation's list of instances. The method then returns a tuple containing the list of all parsed events and the UUID-validator mapping.

#### `add_validator(self, event)`:

- `event` is an Event object which holds the details of the validator that is being added. It includes the validator identifier and its weight.

The `add_validator` method is used to add a new validator to the existing set of validators. This is done by creating a new Lachesis instance for the new validator, initializing it, and updating the various data structures that hold information about the validators, their weights, activation times, and their event queues. The new validator's details are added to the simulation's lists and dictionaries that hold validator data.

#### `process(self)`

The `process` function is an integral method in the `LachesisMultiInstance` class, implementing a comprehensive processing pipeline for a collection of events. This method sorts these events by their timestamps, and then processes them sequentially. It adjusts the validator set by activating and deactivating validators at appropriate frames based on the events, and manages the propagation of these events across all active validator instances.

The primary steps that this function performs include:

1. **Event Initialization and Sorting:** Events are first parsed and initialized into a list (`event_list`) and a map (`uuid_validator_map`). They are then sorted by their timestamps into a dictionary (`timestamp_event_dict`), ensuring chronological order of processing.
2. **Frame Tracking:** Tracks and updates frame-related variables such as `minimum_frame`, `maximum_frame`, and `validator_highest_frame`. These frame references are critical for managing validator activation and deactivation, ensuring validators are activated or deactivated at the correct frame and time.
3. **Event Processing per Timestamp:** The events happening at the current timestamp are processed. During processing, the method performs a range of operations:
    - Direct parents of each event are verified and recorded.
    - If an event is the last event from a validator, relevant deactivation details are recorded and the validator is added to the `deactivation_queue`.
    - If the validator associated with an event has not yet been seen and the event's timestamp is within the field of view, the validator is queued for activation. The initial frame and weight for the validator are recorded in `activation_queue`.
    - For validators that are in the activation queue, if the current minimum frame is greater than or equal to the frame at which the validator was planned to be activated, the validator is added to the `instances`.
    - If an event is associated with a validator instance and it falls within the time scope, the event is passed to that instance for further processing via [`defer_event`](https://github.com/machin3boy/Lachesis/tree/main/PyLachesis#defer_eventself-event-instances-uuid_validator_map).
4. **Request Queue Processing:** [Processes any queued requests](https://github.com/machin3boy/Lachesis/tree/main/PyLachesis#process_request_queueself-instances) in all the validator instances.
5. **Deferred Event Processing**: [Processes any deferred events](https://github.com/machin3boy/Lachesis/tree/main/PyLachesis#process_deferred_eventsself) in all the validator instances.

This method ensures that events are processed in a chronological order and are propagated correctly across the various validator instances. Moreover, the method accurately manages validator activations and deactivations based on the events and their timestamps, thereby maintaining an up-to-date and accurate picture of the network's state. 

#### `run_lachesis_multiinstance(self, input_filename, output_folder, graph_results=False)`

The `run_lachesis_multiinstance` method functions as a main driver to execute the Lachesis protocol in a multi-instance scenario. This method processes a collection of events for each validator instance, based on data from an input file. Optionally, it can generate individual graph results for each validator instance. The method also verifies the consistency of each instance with a reference instance, ensuring the accuracy of the protocol's execution.

- `input_filename`: This is the name of the input file that contains the event data to be processed. The data in this file is parsed into a list of events, with each event containing details about the validator, timestamp, sequence, etc.
- `output_folder`: This is the folder where individual graphical representations of the final state of each validator instance will be saved, provided that `graph_results` is set to True.
- `graph_results`: This is a Boolean parameter that determines whether or not to generate graphical representations of the final state for each validator instance. If set to True, a graph will be generated and saved for each validator instance in the `output_folder`.

The steps followed by this function are as follows:

1. **Setup**: The method sets up input file path and the `graph_results` flag. The `process` method of `LachesisMultiInstance` is called to process the events for each validator instance.
2. **Reference Instance Creation**: A reference instance is created by running the Lachesis protocol using the `run_lachesis` method on the input file. This serves as a reference for verifying the multi-instance run.
3. **Graph Result Generation**: If `graph_results` is set to True, the method iterates over each validator instance and generates a graph of the final state of the protocol. These graphs are saved as PDF files in the `output_folder`, with individual files for each validator instance.
4. **Verification**: The method then verifies the accuracy and consistency of each validator instance in relation to the reference instance. Several aspects are verified such as frame, block, time, frame to decide, quorum cache, root set validators, events, root set events, validator cheater list, and atropos roots. If any inconsistency is detected, an assertion error will be raised, indicating the specific inconsistency.

This method is important for testing and verifying the Lachesis protocol in scenarios where multiple validator instances are active simultaneously. It provides a means to evaluate the protocol's ability to maintain consistency and accuracy across different instances to verify that the consensus algorithm functions deterministically.

### class Lachesis

The Lachesis class serves as the core entity that encapsulates the individual processing of each validator in the Lachesis consensus protocol. This involves managing and processing incoming events from the Directed Acyclic Graph (DAG), executing the protocol to assign attributes like frames and blocks to the events, and identifying special events such as roots or Atropos roots.

The Lachesis class also plays a crucial role in handling suspected anomalies or exceptions, such as identifying and managing cheater events. It is equipped with methods that maintain the integrity of the consensus process by detecting forks and rectifying the anomalies associated with them.

Furthermore, this class enables the inter-validator communication necessary for the functioning of the protocol. It can request missing Events in the DAG from other validators and respond to similar requests from them. This is a key aspect of ensuring that each instance of the Lachesis class maintains a coherent and updated view of the Event DAG, thereby ensuring accurate consensus.

The associated methods, to be described in detail, each perform a unique function contributing to these responsibilities, from initialization and deferring of events, to quorum calculation, root identification, voting, fork detection, and graphing results, culminating in the execution of the Lachesis protocol.

#### `__init__(self, validator=None)`

This is the constructor of the Lachesis class object. It initializes various properties essential for consensus tracking.

- `validator` is the optional parameter which represents the associated validator for this instance of the Lachesis class. The reason it defaults to None is to accommodate two modes of running the Lachesis consensus. The "global" mode allows the Lachesis instance to process and have knowledge of all events directly. Conversely, in the "individual" mode, each validator is aware of only the events it directly observes or requests and receives. This facilitates the construction of its unique view of the DAG and subsequent results. This parameter determines the mode of operation.

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
    "decided": True/False,      # tracks if a quorum of validators also voted for this candidate
    "yes": True/False           # tracks the decision to elect this candidate as an Atropos
}

# tracks how roots in a given frame being decided voted for Atropos candidates
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
- `leaves` tracks the leaves of the DAG - that is, those Events that are not the parents of any other event in the DAG. This is to facilitate returning the subgraph of Events unknown to another validator more efficiently by iterating towards the direct parents from the leaves to determine which Events to return.

#### `initialize_validators(self, validators=None, validator_weights=None)`:

This is the method that sets the validators and their corresponding weights when a Lachesis instance is initializing.

- `validators` is the list of validators to initialize that the validators are aware of as they are in the `field_of_view` of the test case DAG
- `validator_weights` is the variable to track the weights of the corresponding validators

#### `defer_event(self, event, instances, uuid_validator_map)`

The `defer_event` method manages the process of deferring the processing of an Event until its parent Events have been established within the DAG or process queue.

On invocation, the method checks the UUIDv4s of the Event's parent events. If a parent Event's UUIDv4 is found within the instance's `process_queue` or `uuid_event_dict`, it implies that the parent Event has either been requested previously or is already present.

However, if a parent Event is not present, the `defer_event` method initiates a request from the validator associated with the missing parent Event. This check-and-request process is executed for each parent UUID related to the Event.

This method ensures the correct sequence of event processing by safeguarding against scenarios where a parent event, which should logically precede, has not been processed yet.

- `event` is the Event that is currently being deferred and the parents of which are being checked.
- `instances` is the dictionary of validator:instance key-value pairs of validators' corresponding Lachesis instance objects to request events from.
- `uuid_validator_map` is the mapping of UUIDv4s to validators to determine which validator corresponds to the parent UUIDv4.

#### `process_request_queue(self, instances)`

The `process_request_queue` method operates by scanning its `request_queue`, which holds tuples in the format (validator, UUIDv4). Its primary function is to deliver the portion of the DAG that is absent in the requesting validator's view.

It returns those Events from its DAG that have a timestamp less than the Event associated with the requested UUIDv4, with one exception. For Events belonging to the validator that generated the UUIDv4 in question, the timestamp could be equal to or less than the timestamp of the requested Event. In summary, this method helps ensure all validators are supplied with the necessary preceding Events, thereby maintaining an accurate representation of the DAG.

The method achieves this by iterating from each of its leaf nodes in the DAG, tracked by the `leaves` property, towards its direct parents, stopping once an Event is encountered that is present in the requesting validator. All Events that match the timestamp requirement and are missing from the requesting validator are added to the requesting validator's `process_queue`. 

- `instances` is the dictionary of validator:instance key-value pairs of validators' corresponding Lachesis instance objects to request events from.

#### `process_deferred_events(self)`

The process_deferred_events method is in charge of invoking the process_events function of the corresponding Lachesis instance. This function processes all the Events scheduled to be incorporated into the validator's DAG and evaluated for consensus. Once this operation is complete, the method clears the process_queue, ensuring all deferred Events have been duly addressed and the queue is ready for the next set of Events.

#### `quorum(self, frame)`

The quorum method calculates the weight of the quorum for a given frame in the DAG. It primarily takes into account the set of active validators and their respective weights, while also considering any changes in validator activity or suspected misbehavior.

- `frame` is the frame for which the quorum is calculated and stored in the cache, or returned if it is already available in the cache.

The method uses a cache, `quorum_cache`, to store the calculated quorum weights for different frames to avoid unnecessary computations.

The method proceeds as follows:

- Initially, it makes copies of the sets of deactivated cheaters and validators. It then iterates over the `deactivation_queue`, a dictionary that keeps track of validators that are to be deactivated and the frame at which they should be deactivated. Validators that have reached or surpassed their deactivation frame are added to the `deactivated_validators` set.
- An `active_validators` list is constructed, which includes validators who are not in either the `deactivated_cheaters` or `deactivated_validators` sets.
- Next, the method handles suspected cheaters. It iterates over the `suspected_cheaters` set, checking if a suspected cheater is not already deactivated. If not, it checks whether this suspected cheater has been observed by the majority of the active validators before `frame - 1` - this is akin to a buffer zone to ensure all validators have had the chance to observe the cheater in question. If this cheater has been observed by the majority of active validators, it is added to the `deactivated_cheaters` set.
- The method then processes the `activation_queue`, a dictionary with validators that are to be activated and their respective weights. If a validator's activation frame is equal to or earlier than the current frame and they're not already an active validator, they are added to the validators list and their weight is set.
- Finally, the method calculates the total weight of active validators that are not deactivated, either as cheaters or validators, and that are not still to be activated. This total weight is then used to calculate the weight of the quorum for the current frame, which is defined as `2 * weights_total // 3 + 1`.

The quorum weight for the current frame is cached and returned. This represents the minimum amount of validator weight needed to reach a consensus for the frame in question.


#### `is_root(self, event)`

The `is_root` method is responsible for determining if a given Event in the DAG can be considered as a root. By definition, an Event is considered a root if it has been [forkless-caused](https://github.com/machin3boy/Lachesis/tree/main/PyLachesis#forkless_cause) by the prior frame's quorum of roots, or if it is the first Event of the validator in question.

- `event`: the Event being examined in order to determine if it can be classified as a root.

Here are the steps the method takes to determine if an Event is a root:

- If the sequence number of the `Event` is 1, the Event is deemed a root immediately. This is because the first Event in a sequence is always considered a root.
- The Event's frame number is fetched from the `validator_highest_frame` dictionary (which maintains the highest frame each validator has reached), or set to `1` if this is the validator's first event.
- The method fetches the root Events for the Event's frame from the `root_set_events` dictionary. If there are no root Events for this frame, the function returns `False`, indicating the Event is not a root.
- The method calculates the total weight of the root Events that 'forkless-cause' this Event. 
- Finally, the method checks whether the total weight of the roots it is 'forkless-caused' by is equal to or surpasses the quorum for the frame. If it does, the method returns `True`, meaning the Event is a root. If not, the function returns `False`.

This method plays an essential role in the operation of Lachesis by helping to identify root Events, which aids in structuring the DAG into a set of consecutive frames.

#### `set_roots(self, event)`

The `set_roots` method is utilized to determine whether a given Event qualifies as a root and accordingly update the frame structures in the DAG. If an Event is indeed a root, the method designates it as such and properly sets its frame in addition to updating the `root_set_events`, `root_set_validators`, and `validator_highest_frame` records.

- `event`: the Event which is being analyzed to ascertain whether it should be designated as a root.

The method proceeds as follows:

- It uses the `is_root` method to check if the Event is a root. If it isn't, the function updates the `validator_highest_frame` dictionary and ends its execution.
- If the Event is a root, the method marks it as such (`event.root = True`). If the Event is the first in its sequence, its frame is set to 1, or to the activation frame of the validator if it is present in the `activation_queue`. For all other roots, the frame number is incremented by 1 from its current frame.
- The method then checks if the current frame of the `Lachesis` object is less than the Event's frame. If so, it updates the current frame to the Event's frame.
- Following this, the method updates `root_set_events` and `root_set_validators` dictionaries, adding the Event to the list of root events for its frame, and the validator to the list of root validators for the frame.
- If the frame of the Event does not already exist in `root_set_events`, the method also calls `quorum` to calculate the quorum for this new frame.
- Finally, the method updates the `validator_highest_frame` dictionary to record the highest frame number the validator has reached.

This method plays a pivotal role in maintaining the frame structure of the DAG and assists in identifying the roots, which are the backbone for creating a topological ordering of the Events.

#### `atropos_voting(self, new_root)`

The `atropos_voting` method conducts a voting process to determine the Atropos for each frame within the Directed Acyclic Graph (DAG). An Atropos is a unique root Event that represents the head of a finalized frame, or block.

- `new_root`: This is the root Event for which the voting process is being conducted.

Here's the breakdown of the method's operations:

- It begins by fetching all root candidates eligible for becoming the Atropos of the frame under consideration (`frame_to_decide`).
- The method then loops through each candidate. If a candidate's UUID is already in `decided_roots`, it is skipped since its status has already been determined.
- For each candidate root, the method prepares a vote. The structure of the vote depends on the frame number of the `new_root` relative to the frame to decide.
  - If `new_root`'s frame directly succeeds the frame to decide, then this is the first round and the vote is simply whether `new_root` is forkless-caused by the candidate.
  - If `new_root`'s frame surpasses the frame to decide by more than one, then this is the second round or more, and the vote takes into account the voting of previous roots in the frame before `new_root`'s frame. The method tallies up the weight of the 'yes' and 'no' votes from the previous roots. The vote is then determined by whether the 'yes' or 'no' votes surpass the quorum for the frame.
- The voting result is then stored in the `election_votes` data structure. If the vote is 'decided' (i.e., either 'yes' or 'no' votes reach a quorum), the result is also stored in the `decided_roots` dictionary.

This method plays a key role in determining the Atropos for each frame, which is a critical step in dividing the Events into chronologically ordered blocks and finalizing frames.

#### `process_known_roots(self)`

The `process_known_roots` method is responsible for the orderly processing of known root Events to determine the Atropos for each successive frame to decide in the DAG.

Here is how the method works:

- The method iterates over each frame starting from the frame following the last decided frame (`frame_to_decide`) up to the current frame in the DAG (`self.frame`).
- For each frame, it retrieves the set of root Events.
- For each root Event, the method invokes the `atropos_voting` method. 

This method ensures that all known root Events are orderly processed and voted upon to determine the Atropos of each frame. By doing so, it plays an instrumental role in structuring the DAG into a set of chronological blocks.

#### `forkless_cause(self, event_a, event_b)`

The `forkless_cause` method checks if `Event A` is forkless caused by `Event B` under certain conditions in the Directed Acyclic Graph (DAG) of the Events.

- `event_a` and `event_b`: The two Events for which the forkless causality relation is being evaluated.

The method operates as follows:

- First, it checks if the validator of `Event B` is in the cheater list for the validator of `Event A` and if the timestamp of the first cheating event is less than or equal to the timestamp of `Event A` - the latter condition is important for deterministic computation between validators retrieiving events at different times, as this method assumes that `A`'s validator only has knowledge of `B`'s Events up to its timestamp. If these conditions are met, it returns `False`, as `Event B` doesn't forkless-cause `Event A`.
- The method then initializes a dictionary `a` that holds the highest sequence numbers observed by each validator in `Event A` and a dictionary `b` that represents the lowest observing sequence numbers of validators in `Event B`.
- Subsequently, it iterates over the validators and their observed sequence numbers in dictionary `a`. If a validator and its observed sequence number also exist in `b` and the sequence number in `b` is less than or equal to that in `a`, it checks whether `Event A` and `Event B` form a branch without any forks (a 'forkless' branch). This is done by determining whether `Event A` and `Event B` both exist in the events visited by a validator and no forks were observed by the validator of `Event A`.
- If `Event A` and `Event B` form a forkless branch, the weight of the validator is added to the total count (`yes`).
- Finally, the method checks whether the count of the weights of the validators observing `Event B` in a forkless manner (i.e., without any forks) reaches a quorum for the frame of `Event B`. If it does, the function returns `True` indicating `Event B` forkless-causes `Event A` or that `Event A` is forkless-caused by `Evebt B`. Otherwise, it returns `False`.

This mechanism, known as forkless causality, plays a key role in maintaining the integrity of the DAG and is essential in the formation of consensus in the Lachesis protocol. This method provides the core logic that allows the Lachesis protocol to ensure the forkless causality between Events and helps in maintaining the acyclicity and integrity of the Event graph.

**Formal Definition:**

Event `A` is said to be forkless-caused by Event `B` if the following conditions are met within the subgraph of `A` (the subgraph of `A` being all Events reachable by `A`):

1. `Event A` does not observe any forks from the validator of `Event B`.
2. A quorum of validators, defined as (⌈⅔W⌉ +1) where W represents the total weight of validators, has observed `Event B` without detecting any forks.


#### `detect_forks(self, event)`

The `detect_forks` method identifies if a fork has occurred within the Directed Acyclic Graph (DAG) of the Events, and keeps a record of validators who have created a fork. A fork is a situation where a validator creates two or more events with the same sequence and epoch number. This implementation has not yet implemented epochs and as a consequence of ever-increasing sequences, only sequences are examined.

- `event` is the Event which scans its parents for forks by examining and updating its `visited` dictionary and other data structures. 

The method performs the following steps:

- It first checks if the validator of the Event is already listed in the cheater list or in the frames of cheaters as a key, and if not, it initializes these entries for the validator.
- The method then creates a deque of the parent Events of the current Event and enters a loop, which continues until all parent Events have been processed.
- In each iteration of the loop, the method pops a parent Event from the deque and processes it. If the validator of the Event has not visited the parent Event yet, the method marks the parent Event as visited and adds it to the set of Events visited by the validator.
- The method then checks if the sequence number of the parent Event has been observed by the validator before. If it has, this indicates a fork, and the method updates the cheater list, the frames of cheaters, the timestamp of cheaters, and the suspected cheaters set accordingly.
- If the sequence number of the parent event has not been observed by the validator before, the method adds the sequence number to the observed sequences of the validator.
- Finally, the method extends the deque of parent events with the parents of the current parent event, allowing the process to continue for all ancestors of the initial event.

This function allows the Lachesis protocol to detect forks and manage cheaters effectively, ensuring the integrity and reliability of the network.

**Fork and Cheater Definition:**

In the context of the Lachesis protocol, a fork refers to a pair of events produced by the same validator with the same sequence and epoch number. The validator which creates a fork is called a cheater. Events from forks are excluded from root finding, thereby maintaining the integrity of the frames and the validity of the consensus process.

#### `set_highest_events_observed(self, event)`

The `set_highest_events_observed` method updates the `highest_observed` attribute for a given Event. The `highest_observed` attribute represents the most recent Event created by each validator that is reachable by the given Event.

- `event` is the Event for which the `highest_observed` attribute is being updated.

Here's the breakdown of the method's operations:

- The method starts by iterating over each parent of the `event`.
- For each parent, it first checks whether the parent's validator is not in `event.highest_observed` or if the parent's sequence number is higher than the current highest observed sequence number of the validator. It also checks whether the parent's UUID is less than the current highest observed UUID in case of a sequence number tie. If any of these conditions are met, it updates `event.highest_observed` for the parent's validator with the UUID and sequence number of the parent.
- Next, the method iterates over each `highest_observed` entry of the parent. For each of these, it performs a similar set of checks as before to determine if the `highest_observed` attribute for the given validator needs to be updated. If necessary, it updates `event.highest_observed` for the validator with the observed information from the parent.

This method ensures that the `highest_observed` attribute for each Event is accurately maintained, enabling the protocol to keep track of the most recent Event from each validator that is reachable by a given Event. 

#### `set_lowest_observing_events(self, event)`

The `set_lowest_observing_events` method updates the `lowest_observing` attribute for a given Event's ancestors in the Directed Acyclic Graph (DAG). The `lowest_observing` attribute represents the earliest Event created by each validator that observes a given Event.

- `event` refers to the Event from which observations are drawn to update the `lowest_observing` attribute of its ancestor Events in the Directed Acyclic Graph (DAG).

Here's the breakdown of the method's operations:

- The method begins by setting up a queue with the parents of the `event`.
- It then enters a loop, popping parents from the queue one by one. For each parent, it checks if the `event`'s validator is not in the parent's `lowest_observing` list, or if the `event`'s sequence number is less than the currently lowest observed sequence number for the validator. It also checks whether the `event`'s UUID is less than the current lowest observed UUID in case of a sequence number tie. If any of these conditions are met, it updates `parent.lowest_observing` for the `event`'s validator with the UUID and sequence number of the `event`.
- If the `event`'s validator and the parent's validator are in the `validator_cheater_list`, and the current time surpasses the timestamp at which they were added to the cheater list, the method skips the current iteration and continues with the next parent.
- Otherwise, it extends the queue with the current parent's parents, ensuring all ancestors of the `event` are covered in the process.

This method ensures that the `lowest_observing` attribute for each Event's ancestors is accurately maintained, which helps in establishing the sequence of Events observed by each validator.

#### `process_events(self, events)`

The `process_events` function is a comprehensive method that processes a list of incoming Events. This method sorts these events by their timestamps and sequentially incorporates them into the Directed Acyclic Graph (DAG).

- `events` is the list of Events to incorporate into the DAG of the validator and to evaluate consensus mechanisms for.

The key operations that this function performs include:

1. **Timestamp Sorting:** Events are sorted by their timestamps, ensuring chronological order of processing.
2. **Frame Management:** Manages frame-related variables including `minimum_frame`, `maximum_frame`, and `validator_highest_frame`. These frame references are critical for managing validator activation and deactivation, ensuring validators are activated or deactivated at the appropriate frame and time (deterministically).
3. **Event Sorting and Processing:** The events happening at the current timestamp are sorted and processed. During processing:
    - Direct parents of each event are identified and recorded.
    - Leaf events are updated (events that have no child events yet).
    - If an event is the last event from its validator, relevant deactivation details are recorded.
    - The validator of the event is verified. If the validator is new and within the field of view, they are added to the validator list and their weight is recorded. If it's beyond the field of view, the validator is queued for activation.
4. **Fork Detection, Observation Updates, and Root Setting:** Forks in the event's history are detected, the highest observed events and lowest observing events for each event are updated, and roots of the DAG are also updated with the new event.
5. **Event Incorporation:** The event is added to the `events` list, its UUID to the `uuid_event_dict` dictionary for easy retrieval, and any known roots are processed.

#### `graph_results(self, output_filename)`

The `graph_results` method is a helper function primarily used for graphing the results of the consensus algorithm. It provides a visual representation of the constructed Directed Acyclic Graph (DAG) showing the events processed, their relationships, their validators, and any additional attributes such as roots or atropos. The method color codes each node in the graph based on specific attributes, and generates a comprehensive visualization that helps in understanding the flow and structure of the DAG. 

- `output_filename` is the file name passed to the method to indicate where to save the visual representation of the results.

The graph output by this method can be very useful for understanding the performance and progression of the consensus algorithm over time. It includes all events (unless they are by suspected cheaters), their relationships with parent events, and key characteristics like frame, weight, root, and atropos status. It uses matplotlib to create and save the graph as a PDF file, with a filename passed to the method as a parameter. 

In the graph, different colors are used to represent different frames, with a distinct shade used for atropos events. This provides a clear visual distinction between different stages of the algorithm. The size of the graph adjusts dynamically based on the number of nodes and levels in the DAG to ensure the best possible visual representation.



## `automate_lachesis.py`

The `automate_lachesis.py`script aids in automating tests by utilizing the `automate_lachesis()` function.

#### automate_lachesis(input_dir, output_dir, create_graph=False, create_graph_multi=False)


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