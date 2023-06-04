import dataclasses
import enum
import sys
import math
from collections.abc import Set
from typing import List


def print_debug(msg):
    print(msg, file=sys.stderr, flush=True)

#### CHATGPT
# Helper function to find the node with the minimum distance
def find_min_distance(distances, visited):
    min_distance = float('inf')
    min_node = None
    for node in distances:
        if distances[node] < min_distance and not visited[node]:
            min_distance = distances[node]
            min_node = node
    return min_node

# Dijkstra's algorithm implementation
def dijkstra(graph, start):
    distances = {i: float('inf') for i in range(len(graph))}
    distances[start] = 0
    visited = {i: False for i in range(len(graph))}

    while True:
        node = find_min_distance(distances, visited)
        if node is None:
            break
        visited[node] = True
        for neighbor in graph[node].neighbors:
            new_distance = distances[node] + 1
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance

    return distances

# Find the shortest path between start and destinations
def find_shortest_path(graph, start, destinations):
    shortest_paths = {}
    distances = dijkstra(graph, start)
    for dest in destinations:
        path = [dest]
        node = dest
        while node != start:
            for neighbor in graph[node].neighbors:
                if distances[node] == distances[neighbor] + 1:
                    path.insert(0, neighbor)
                    node = neighbor
                    break
        shortest_paths[dest] = path
    return shortest_paths

###

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


class Commands(enum.Enum):
    BEACON = "BEACON"
    LINE = "LINE"
    WAIT = "WAIT"
    MESSAGE = "MESSAGE"


class CellType(enum.Enum):
    EMPTY = 0
    EGGS = 1
    CRYSTAL = 2


@dataclasses.dataclass
class Cell:
    type_: CellType
    resources: int
    neighbors: Set[int] = dataclasses.field(default_factory=set)
    my_ants: int = 0
    opp_ants: int = 0


number_of_cells = int(input())  # amount of hexagonal cells in this map
cells = []
crystals = []
eggs = []
for i in range(number_of_cells):
    # _type: 0 for empty, 1 for eggs, 2 for crystal
    # initial_resources: the initial amount of eggs/crystals on this cell
    # neigh_0: the index of the neighbouring cell for each direction
    _type, initial_resources, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    cell_type = CellType(_type)
    neighbors = {neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5}
    neighbors.discard(-1)

    cell = Cell(cell_type, initial_resources, neighbors)
    cells.append(cell)

    if cell.type_ == CellType.CRYSTAL:
        crystals.append(i)
    elif cell.type_ == CellType.EGGS:
        eggs.append(i)


my_bases = set()
number_of_bases = int(input())
for i in input().split():
    my_base_index = int(i)
    my_bases.add(my_base_index)

opp_bases = []
for i in input().split():
    opp_base_index = int(i)
    opp_bases.append(opp_base_index)

crystals_and_eggs = crystals + eggs
closest_crystals = {}
closest_eggs = {}
for base_idx in my_bases:
    closest_map = find_shortest_path(cells, base_idx, crystals_and_eggs)
    closest_crystals_map = {k: v for k, v in closest_map.items() if k in crystals}
    closest_crystals[base_idx] = sorted(list(closest_crystals_map.items()), key=lambda x: len(x[1]))

    closest_eggs_map = {k: v for k, v in closest_map.items() if k in eggs}
    closest_eggs[base_idx] = sorted(list(closest_eggs_map.items()), key=lambda x: len(x[1]))

# game loop
starting_ants = 0
while True:
    my_ants_count = 0
    for i in range(number_of_cells):
        # resources: the current amount of eggs/crystals on this cell
        # my_ants: the amount of your ants on this cell
        # opp_ants: the amount of opponent ants on this cell
        resources, my_ants, opp_ants = [int(j) for j in input().split()]
        cells[i].resources = resources
        cells[i].my_ants = my_ants
        cells[i].opp_ants = opp_ants
        my_ants_count += my_ants

    if starting_ants == 0:
        starting_ants = my_ants_count

    cmd = ""
    for opp_base_idx, base_idx in enumerate(my_bases):
        for idx in range(len(closest_crystals[base_idx])-1, -1, -1):
            if cells[closest_crystals[base_idx][idx][0]].resources == 0:
                del closest_crystals[base_idx][idx]

        for idx in range(len(closest_eggs[base_idx])-1, -1, -1):
            if cells[closest_eggs[base_idx][idx][0]].resources == 0:
                del closest_eggs[base_idx][idx]

        # num_crystals = 3 + int(not bool(closest_eggs[base_idx])) * 2
        should_attack = False
        num_crystals = math.ceil(my_ants_count / (starting_ants * 1.0))
        if closest_eggs[base_idx]:
            num_eggs = math.ceil(my_ants_count / (starting_ants * 2.0)) + 1
        else:
            num_eggs = 0
            should_attack = True

        print_debug(f"num_crystals = {num_crystals}, num_eggs = {num_eggs}")

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        for i in range(num_crystals):
            if i >= len(closest_crystals[base_idx]):
                break

            if cmd:
                cmd += "; "

            cmd += f"{Commands.LINE.value} {base_idx} {closest_crystals[base_idx][i][0]} 2"

        for i in range(num_eggs):
            if i >= len(closest_eggs[base_idx]):
                break

            if cmd:
                cmd += "; "

            cmd += f"{Commands.LINE.value} {base_idx} {closest_eggs[base_idx][i][0]} 1"

        if should_attack:
            if cmd:
                cmd += "; "

            cmd += f"{Commands.BEACON.value} {opp_bases[opp_base_idx]} 2"

    if cmd:
        cmd += "; "
    cmd += f"{Commands.MESSAGE.value} gl hf"

    print(cmd)

    # WAIT | LINE <sourceIdx> <targetIdx> <strength> | BEACON <cellIdx> <strength> | MESSAGE <text>
    # print("WAIT")
