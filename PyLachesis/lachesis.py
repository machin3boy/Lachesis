import random
from sortedcontainers import SortedSet
from collections import deque
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx


def convert_input_to_DAG(input_file):
    nodes = []

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            parts = line.split(";")

            node_info = parts[0].strip()[6:-1]
            node_id, timestamp, predecessors = node_info.split(",")
            timestamp, predecessors = int(timestamp), int(predecessors)
            node_key = (node_id[1:], predecessors)

            node = Node(node_key, timestamp, predecessors)
            nodes.append(node)

            for child_info in parts[1:]:
                child_info = child_info.strip()[7:-1]
                child_info_parts = child_info.split(",")
                if len(child_info_parts) < 2:
                    continue
                child_id, child_timestamp = child_info_parts[:2]
                child_timestamp = int(child_timestamp)
                child_predecessors = int(child_info_parts[2])
                child_key = (child_id[1:], child_predecessors)

                child = Node(child_key, child_timestamp, child_predecessors)
                node.children.append(child)

    return nodes


class LachesisMultiInstance:
    def __init__(self):
        self.instances = {}
        self.nodes = []

    def initialize_instances(self):
        validators = set(node.id[0] for node in self.nodes)
        for validator in validators:
            self.instances[validator] = Lachesis(validator)
            self.instances[validator].validators = validators.copy()

            self.instances[validator].validator_weights = {
                v: next(node for node in self.nodes if node.id[0] == v).weight
                for v in validators
            }
            self.instances[validator].root_set_validators[1] = validators.copy()

    def process_graph_by_timesteps(self):
        max_timestamp = max(node.timestamp for node in self.nodes)

        for current_time in range(max_timestamp + 1):
            nodes_to_process = [
                node for node in self.nodes if node.timestamp == current_time
            ]

            random.shuffle(nodes_to_process)

            for node in nodes_to_process:
                validator = node.id[0]
                seq = node.predecessors

                event = Event(
                    id=(validator, seq),
                    seq=seq,
                    creator=validator,
                    parents=[(parent.id) for parent in node.children],
                )

                instance = self.instances[validator]
                # instance.events[event.id] = event
                if event.id not in instance.event_timestamps:
                    instance.event_timestamps[event.id] = []
                instance.event_timestamps[event.id].append(current_time)
                instance.defer_event_processing(event, self.instances)

            for instance in self.instances.values():
                instance.process_request_queue(self.instances)

            for instance in self.instances.values():
                instance.process_deferred_events()

            for instance in self.instances.values():
                instance.time += 1

        return self.instances

    def run_lachesis_multi_instance(self, input_file, output_file, create_graph=False):
        nodes = convert_input_to_DAG(input_file)
        self.nodes = nodes
        self.initialize_instances()
        self.process_graph_by_timesteps()

        if create_graph:
            for instance in self.instances.values():
                output_file_validator = instance.validator + "_" + output_file
                instance.graph_results(output_file_validator)


class Node:
    def __init__(self, id, timestamp, predecessors):
        self.id = id
        self.timestamp = timestamp
        self.predecessors = predecessors
        self.children = []
        self.weight = 1

    def __repr__(self):
        return f"Node({self.id}, {self.timestamp}, {self.predecessors})"


class Event:
    def __init__(self, id, seq, creator, parents, frame=None, count=0):
        self.id = id
        self.seq = seq
        self.creator = creator
        self.parents = parents
        self.lowest_events_vector = {}
        self.highest_events_observed_by_event = {}
        self.frame = frame
        self.count = count

    def copy_basic_properties(self):
        return Event(
            id=self.id,
            seq=self.seq,
            creator=self.creator,
            parents=self.parents,
        )


class Lachesis:
    def __init__(self, validator=None):
        self.frame = 1
        self.block = 1
        self.epoch = 1
        self.root_set_validators = {}
        self.root_set_nodes = {}
        self.election_votes = {}
        self.frame_to_decide = 1
        self.cheater_list = set()
        self.validator = validator
        self.validators = set()
        self.validator_weights = {}
        self.time = 0
        self.events = {}
        self.event_timestamps = {}
        self.timestep_nodes = []
        self.decided_roots = {}
        self.atropos_roots = {}
        self.last_validator_sequence = {}
        self.request_queue = deque()
        self.process_queue = {}
        self.quorum_values = {}
        self.next_event_index = {}
        self.event_parents = {}
        self.event_timestamp_indices = {}

    def defer_event_processing(self, event, instances):
        existing_events = self.process_queue.get(event.id, [])

        if not existing_events:
            self.process_queue[event.id] = [event]
        else:
            # Add the new event without merging parents
            self.process_queue[event.id].append(event)

        # if event.id not in self.event_timestamps:
        #     self.event_timestamps[event.id] = []
        # self.event_timestamps[event.id].append(self.time)

        # Store the parents of the deferred event
        if event.id not in self.event_parents:
            self.event_parents[event.id] = []
        self.event_parents[event.id].append(event.parents)

        for parent_id in event.parents:
            if parent_id not in self.events and parent_id not in self.process_queue:
                parent_instance = instances[parent_id[0]]
                parent_instance.request_queue.append((event.creator, [parent_id]))

        for existing_event in existing_events:
            for parent_id in existing_event.parents:
                if parent_id not in self.events and parent_id not in self.process_queue:
                    parent_instance = instances[parent_id[0]]
                    parent_instance.request_queue.append((event.creator, [parent_id]))

    def process_deferred_events(self):
        for event_id in self.process_queue:
            if event_id not in self.next_event_index:
                self.next_event_index[event_id] = 0

        sorted_process_queue = sorted(
            self.process_queue.items(),
            key=lambda x: (
                self.event_timestamps[x[0]][self.next_event_index[x[0]]],
                x[0],
            ),
        )

        # print()
        # print("SORTED PROCESS QUEUE")
        # print(self.event_timestamps, self.next_event_index)

        for event_id, events in sorted_process_queue:
            for event in events:
                # Reference the correct parents for the event at the current index, if available
                if event.id in self.event_parents:
                    event.parents = self.event_parents[event.id][
                        self.next_event_index[event.id]
                    ]
                # print("DEFERRED EVENTS")
                # print(event.id, event.parents)
                self.process_event(event)
                self.next_event_index[event.id] += 1
            del self.process_queue[event_id]

    def process_request_queue(self, instances):
        while self.request_queue:
            recipient_id, missing_event_ids = self.request_queue.popleft()

            recipient_instance = instances[recipient_id]
            for event_id in missing_event_ids:
                if event_id[0] in recipient_instance.cheater_list:
                    continue

                if (
                    event_id not in recipient_instance.events
                    and event_id not in recipient_instance.process_queue
                ):
                    missing_event = self.events[event_id].copy_basic_properties()
                    missing_event_timestamp = self.event_timestamps[event_id]

                    if event_id not in recipient_instance.process_queue:
                        recipient_instance.process_queue[event_id] = []

                    recipient_instance.process_queue[event_id].append(missing_event)
                    recipient_instance.event_timestamps[
                        event_id
                    ] = missing_event_timestamp

                    for parent_id in missing_event.parents:
                        if (
                            parent_id not in recipient_instance.events
                            and parent_id not in recipient_instance.process_queue
                        ):
                            self.request_queue.append((recipient_id, [parent_id]))

    def quorum(self, frame_number):
        if frame_number not in self.quorum_values:
            self.quorum_values[frame_number] = (
                2 * sum([self.validator_weights[x] for x in self.validators]) // 3 + 1
            )

        return self.quorum_values[frame_number]

    def highest_events_observed_by_event(self, node):
        for parent_id in node.parents:
            # print()
            # print("self.validator", self.validator)
            # print("\tself.time", self.time)
            # print("\tself.process_queue", self.process_queue)
            # print("\tnode", node.id)
            # print("\tevents", self.events)

            if parent_id[0] in self.cheater_list:
                continue

            parent = self.events[parent_id]

            if (
                parent.creator not in node.highest_events_observed_by_event
                or parent.seq > node.highest_events_observed_by_event[parent.creator]
            ):
                node.highest_events_observed_by_event[parent.creator] = parent.seq

            for creator, seq in parent.highest_events_observed_by_event.items():
                if (
                    creator not in node.highest_events_observed_by_event
                    or seq > node.highest_events_observed_by_event[creator]
                ):
                    node.highest_events_observed_by_event[creator] = seq

    def detect_forks(self, event):
        fork_detected = False

        parent_ids = event.parents

        if event.id in parent_ids:
            self.cheater_list.add(event.creator)
            self.validator_weights[event.creator] = 0
            fork_detected = True

        cheater_validators = set()
        for parent_id in set(parent_ids):
            if parent_ids.count(parent_id) > 1:
                cheater_validator = parent_id[0]
                cheater_validators.add(cheater_validator)

        for cheater_validator in cheater_validators:
            self.cheater_list.add(cheater_validator)
            self.validator_weights[cheater_validator] = 0
            fork_detected = True

        validator = event.creator
        seq = event.seq

        if validator not in self.last_validator_sequence:
            self.last_validator_sequence[validator] = seq
        elif self.last_validator_sequence[validator] < seq:
            self.last_validator_sequence[validator] = seq
        else:
            self.cheater_list.add(validator)
            self.validator_weights[validator] = 0
            fork_detected = True

        return fork_detected

    def forkless_cause(self, event_a, event_b):
        if event_a.id[0] in self.cheater_list or event_b.id[0] in self.cheater_list:
            return False

        a = event_a.highest_events_observed_by_event
        b = event_b.lowest_events_vector

        yes = 0
        for validator, seq in a.items():
            if validator in b and b[validator]["seq"] <= seq:
                yes += self.validator_weights[validator]

        return yes >= self.quorum(event_b.frame)

    def set_lowest_events_vector(self, event):
        parents = deque(event.parents)

        while parents:
            parent_id = parents.popleft()
            if parent_id[0] in self.cheater_list:
                continue
            parent = self.events[parent_id]
            parent_vector = parent.lowest_events_vector

            if event.creator not in parent_vector:
                parent_vector[event.creator] = {"event_id": event.id, "seq": event.seq}

                if event.creator != parent.creator:
                    parents.extend(parent.parents)

    def check_for_roots(self, event):
        if event.seq == 1:
            return True, 1
        else:
            direct_child = self.events[(event.creator, event.seq - 1)]

            if event.creator not in self.cheater_list:
                forkless_cause_current_frame = self.forkless_cause_quorum(
                    event, direct_child.frame
                )
                if forkless_cause_current_frame:
                    return True, direct_child.frame + 1

            return False, None

    def process_event(self, event):
        event.count += 1
        self.events[event.id] = event
        fork_present = self.detect_forks(event)
        if fork_present:
            self.quorum_values[self.frame] = (
                2 * sum([self.validator_weights[x] for x in self.validators]) // 3 + 1
            )

        self.highest_events_observed_by_event(event)
        self.set_lowest_events_vector(event)

        is_root, target_frame = self.check_for_roots(event)
        if is_root:
            if target_frame not in self.root_set_validators:
                self.root_set_validators[target_frame] = SortedSet()
            if target_frame not in self.root_set_nodes:
                self.root_set_nodes[target_frame] = SortedSet()

            event.frame = target_frame

            self.events[event.id].frame = target_frame

            self.frame = target_frame if target_frame > self.frame else self.frame

            if event.creator not in self.cheater_list:
                self.root_set_validators[target_frame].add(event.creator)
                self.root_set_nodes[target_frame].add(event.id)

            self.atropos_voting(event.id)

        else:
            direct_child = self.events[(event.creator, event.seq - 1)]
            event.frame = direct_child.frame

    def forkless_cause_quorum(self, event, frame_number):
        forkless_cause_count = 0
        frame_roots = self.root_set_nodes[frame_number]

        for root in frame_roots:
            root_event = self.events[root]
            if self.forkless_cause(event, root_event):
                forkless_cause_count += self.validator_weights[root_event.creator]

        return forkless_cause_count >= self.quorum(frame_number)

    def atropos_voting(self, new_root):
        candidates = self.root_set_nodes[self.frame_to_decide]
        for candidate in candidates:
            if self.frame_to_decide not in self.election_votes:
                self.election_votes[self.frame_to_decide] = {}
            if (new_root, candidate) not in self.election_votes[self.frame_to_decide]:
                vote = None
                if self.frame == self.frame_to_decide + 1:
                    vote = {
                        "decided": False,
                        "yes": self.forkless_cause(
                            self.events[new_root],
                            self.events[candidate],
                        ),
                    }
                elif self.frame >= self.frame_to_decide + 2:
                    yes_votes = 0
                    no_votes = 0
                    for prev_root in self.root_set_nodes[self.frame - 1]:
                        prev_vote = self.election_votes[self.frame_to_decide].get(
                            (prev_root, candidate), {"yes": False}
                        )
                        if prev_vote["yes"]:
                            yes_votes += self.validator_weights[prev_root[0]]
                        else:
                            no_votes += self.validator_weights[prev_root[0]]

                    vote = {
                        "decided": yes_votes >= self.quorum(self.frame)
                        or no_votes >= self.quorum(self.frame),
                        "yes": yes_votes >= no_votes,
                    }

                if vote is not None:
                    self.election_votes[self.frame_to_decide][
                        (new_root, candidate)
                    ] = vote
                    if vote["decided"]:
                        self.decided_roots[candidate] = vote
                        if vote["yes"]:
                            self.atropos_roots[self.frame_to_decide] = candidate
                            self.frame_to_decide += 1
                            self.block += 1

    def process_graph_by_timesteps(self, nodes):
        sorted_nodes = sorted(nodes, key=lambda node: node.timestamp)
        max_timestamp = max(node.timestamp for node in nodes)
        validators = set(node.id[0] for node in nodes)
        self.root_set_validators[1] = validators
        self.validators = validators
        self.validator_weights = {
            v: next(node for node in sorted_nodes if node.id[0] == v).weight
            for v in validators
        }

        for current_time in range(max_timestamp + 1):
            nodes_to_process = [
                node for node in nodes if node.timestamp == current_time
            ]

            random.shuffle(nodes_to_process)

            for node in nodes_to_process:
                validator = node.id[0]
                seq = node.predecessors

                if validator not in self.validators:
                    self.validators.add(validator)
                    self.validator_weights[validator] = node.weight

                event = Event(
                    id=(validator, seq),
                    seq=seq,
                    creator=validator,
                    parents=[(parent.id) for parent in node.children],
                )

                self.events[event.id] = event

                if event.id not in self.event_timestamps:
                    self.event_timestamps[event.id] = []
                self.event_timestamps[event.id].append(current_time)

                self.process_event(event)

            self.time += 1

        return self

    def darken_color(color, darken_factor):
        r, g, b = color
        r = int(r * darken_factor)
        g = int(g * darken_factor)
        b = int(b * darken_factor)
        return (r, g, b)

    def graph_results(self, output_filename):
        colors = ["orange", "yellow", "blue", "cyan", "purple"]

        colors_rgb = [mcolors.to_rgb(color) for color in colors]

        darker_colors = []
        for color in colors_rgb:
            darker_color = tuple(c * 0.8 for c in color)
            darker_colors.append(darker_color)

        root_set_nodes_new = {}
        for key, values in self.root_set_nodes.items():
            for v in values:
                validator, seq = v
                timestamp = self.event_timestamps[v][-1]
                root_set_nodes_new[(validator, timestamp)] = key

        atropos_roots_new = {}
        for key, value in self.atropos_roots.items():
            validator, seq = value
            timestamp = self.event_timestamps[value][-1]
            atropos_roots_new[(validator, timestamp)] = key

        atropos_colors = ["limegreen", "green"]

        timestamp_dag = nx.DiGraph()

        for node, data in self.events.items():
            validator, seq = node
            timestamp = self.event_timestamps[node][-1]
            frame = data.frame
            weight = self.validator_weights[validator]
            timestamp_dag.add_node(
                (validator, timestamp), seq=seq, frame=frame, weight=weight
            )
            for parent in data.parents:
                if parent in self.events:
                    parent_timestamp = self.event_timestamps[parent][-1]
                    timestamp_dag.add_edge(
                        (validator, timestamp),
                        (parent[0], parent_timestamp),
                    )

        pos = {}
        num_nodes = len(self.validator_weights)
        num_levels = max([node[1] for node in timestamp_dag.nodes])

        figsize = [20, 10]
        if num_levels >= 15:
            figsize[0] = figsize[0] * num_levels / 20
        if num_nodes >= 10:
            figsize[0] = figsize[0] * num_nodes / 4
            figsize[1] = figsize[1] * num_nodes / 10

        fig = plt.figure(figsize=(figsize[0], figsize[1]))
        for i in range(num_nodes + 25):
            for j in range(num_levels + 25):
                node = (chr(i + 65), j)
                pos[node] = (j, i)

        cheater_nodes = [
            (validator, timestamp)
            for validator, timestamp in timestamp_dag.nodes
            if validator in self.cheater_list
        ]
        timestamp_dag.remove_nodes_from(cheater_nodes)

        labels = {
            node: (node[0], node[1], timestamp_dag.nodes[node]["seq"])
            for node in timestamp_dag.nodes
        }

        node_colors = {}
        for node in timestamp_dag.nodes:
            frame = timestamp_dag.nodes[node]["frame"]
            if frame:
                node_colors[node] = colors[frame % len(colors)]
            else:
                node_colors[node] = "black"
            if node in root_set_nodes_new:
                node_colors[node] = darker_colors[root_set_nodes_new[node] % 5]
            if node in atropos_roots_new:
                node_colors[node] = atropos_colors[atropos_roots_new[node] % 2]

        nx.draw(
            timestamp_dag,
            pos,
            with_labels=True,
            labels={
                val: r"$\mathrm{{{}}}_{{{},{}}}$".format(
                    labels[val][0], labels[val][1], labels[val][2]
                )
                for val in labels
            },
            font_family="serif",
            font_size=9,
            node_size=900,
            node_color=[
                node_colors.get(node, node_colors[node])
                for node in timestamp_dag.nodes()
            ],
            font_weight="bold",
        )

        fig.savefig(output_filename, format="pdf", dpi=300, bbox_inches="tight")
        plt.close()

    def run_lachesis(self, graph_file, output_file, create_graph=False):
        nodes = convert_input_to_DAG(graph_file)
        self.process_graph_by_timesteps(nodes)
        if create_graph:
            self.graph_results(output_file)

        sorted_events = sorted(
            self.events.values(), key=lambda e: self.event_timestamps[e.id]
        )

        #     print(f"  Timestamp: {self.event_timestamps[event.id]}")
        #     print(f"  Sequence: {event.seq}")
        #     print(f"  Creator: {event.creator}")
        #     print(f"  Parents: {event.parents}")
        #     print(f"  Lowest Events Vector: {event.lowest_events_vector}")
        #     print(
        #         f"  Highest Events Observed by Event: {event.highest_events_observed_by_event}"
        #     )
        #     print(f"  Frame: {event.frame}")
        #     print("")

        return {
            "graph": graph_file,
            "atropos_roots": self.atropos_roots,
            "frame": self.frame,
            "block": self.block,
            "frame_to_decide": self.frame_to_decide,
            "root_set_nodes": self.root_set_nodes,
            "root_set_validators": self.root_set_validators,
            "election_votes": self.election_votes,
        }


if __name__ == "__main__":
    lachesis_instance = Lachesis()
    lachesis_instance.run_lachesis(
        "../inputs/graphs_with_cheaters/graph_64.txt", "result.pdf", True
    )

    lachesis_multiinstance = LachesisMultiInstance()
    lachesis_multiinstance.run_lachesis_multi_instance(
        "../inputs/graphs_with_cheaters/graph_64.txt", "result_multiinstance.pdf", True
    )
