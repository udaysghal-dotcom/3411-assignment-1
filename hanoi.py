#**********************************************************************
#   hanoi.py
#
#   UNSW CSE
#   COMP3411/9814
#   This code presents the Tower of Hanoi puzzle

# import numpy as np
import copy
import argparse

#**********************************************************************
# Helper functions

# Helper to print start state and actions for solution
def print_solution(start_state, solution):
    start_state.print_state()
    for action, state in solution:
        state.print_action(action)
        state.print_state()

# Create an immutable snapshot of the board state
def create_state_key(state):
    state_key = []
    
    for peg in state.a:
        state_key.append(tuple(peg))
    
    return tuple(state_key)

#**********************************************************************
class State:
    # Is a class attribute and does not live in a single instance
    heuristic_name = "h3a"
    k = [0, 1, 2, 4, 6, 8, 12]

    def __init__(self, a, disks, pegs):
        # Where board and pegs are being stored
        self.a = a
        self.disks = disks
        self.pegs = pegs

        if State.heuristic_name == "h3a":
            self.h = self.heuristic3a()
        elif State.heuristic_name == "h3b":
            self.h = self.heuristic3b()
        else:
            self.h = self.heuristic4a()
    
    def start_state(disks, pegs):
        a = [list(range(1, disks + 1))]
        for p in range(pegs - 1):
            a.append([])
        return (State(a, disks, pegs))

    def is_equal_to(self, other):
        return (self.a == other.a)

    # Check every possible legal move from a given board state
    def expand(self):
        children = []
        for p in range(len(self.a)):
            if self.a[p] != []:
                for q in range(len(self.a)):
                    if self.a[q] == [] or self.a[q][0] > self.a[p][0]:
                        new_a = [peg[:] for peg in self.a]
                        new_a[q].insert(0, new_a[p][0])
                        new_a[p].pop(0)
                        children.append((State(new_a, self.disks, self.pegs), str(new_a[q][0]) + ':' + str(p+1) + '->' + str(q+1),1))
        return children

    # Check if game is won (pre section 1.3)
    def is_goal_old(self):
        for p in range(len(self.a) - 1):
            if self.a[p] != []:
                return False

        return True

    def is_goal(self):
        return self.a[0] == [] and self.a[len(self.a) - 1] == []

    def print_action(self, action):
        print(' ('+action+')')

    def print_state(self):
        print(self.a)

    # Analytically calculate shortest path to sucess
    def heuristic3a(self):
        for c in range(1, self.disks + 1):
            if len(self.a[self.pegs - 1]) < c or self.a[self.pegs - 1][-c] != 1 + self.disks - c:
                return pow(2, self.disks - c)
        return 0

    def heuristic3b(self):
        final_peg = self.a[self.pegs - 1]

        if len(final_peg) == self.disks:
            return 0
        
        if not final_peg:
            return pow(2, self.disks - 1)
        
        if final_peg[-1] < self.disks:
            c = final_peg[-1]
            return pow(2, c - 1) + pow(2, self.disks - 1)
        
        return self.heuristic3a()
    
    def heuristic4a(self):
        final_peg = self.a[self.pegs - 1]

        for c in range(self.disks, 0, -1):
            if c not in final_peg:
                return 1 + State.k[c - 1]
        
        return 0

def ids_depth_limited_search(state, limit, path_set, search_statistics, goal_type="old"):
    if goal_type == "old" and state.is_goal_old():
        return []

    if goal_type == "new" and state.is_goal():
        return []

    if limit == 0:
        # expanded every level
        return None
    
    search_statistics['expanded_paths'] += 1
    for child, action, cost in state.expand():
        state_key = create_state_key(child)

        if state_key in path_set:
            continue

        path_set.add(state_key)
        result = ids_depth_limited_search(child, limit - 1, path_set, search_statistics, goal_type)
        path_set.remove(state_key)

        # reached goal and returned []
        if result is not None:
            curr_action = [(action, child)] + result
            return curr_action
    
    # else did not reach result
    return None

def ids_search(state, goal_type):
    search_statistics = { "expanded_paths": 0 }
    limit = 0
    init_state_key = create_state_key(state)

    while True:
        search_result = ids_depth_limited_search(state, limit, {init_state_key}, search_statistics, goal_type)
        
        if search_result is not None:
            # a path was found, return full path and stats
            return search_result, search_statistics["expanded_paths"]
        
        # if path was not found, increase search depth
        limit += 1
    
    return False

def q1_1_ids_driver(disks, pegs):
    start_state = State.start_state(disks, pegs)
    solution, expanded_paths = ids_search(start_state, "old")
    print(f"Performing iterative deepening search on disks: {disks} and pegs: {pegs}")
    print_solution(start_state, solution)
    
    print(f"Solution length f({disks},{pegs}) = {len(solution)}")
    print(f"Expanded states: {expanded_paths}")

    # placeholder for now, can change 
    return

def q1_3a_ids_driver_k(disks, pegs):
    start_state = State.start_state(disks, pegs)
    solution, expanded_paths = ids_search(start_state, "new")

    print(f"Computing k({disks}) with {pegs} pegs using iterative deepening search")
    print(f"k({disks}) = {len(solution)}")
    print(f"Expanded states: {expanded_paths}")

    return solution, expanded_paths

def ida_star_bounded_search(state, g, bound, path_set, search_statistics):
    f = g + state.h

    if f > bound:
        return None, f
    
    if state.is_goal_old():
        return [], f

    search_statistics["expanded_paths"] += 1
    
    minimum = float("inf")
    for child, action, cost in state.expand():
        state_key = create_state_key(child)

        if state_key in path_set:
            continue
            
        path_set.add(state_key)
        result, value = ida_star_bounded_search(child, g + cost, bound, path_set, search_statistics)
        path_set.remove(state_key)

        if result is not None:
            return [(action, child)] + result, value

        minimum = min(minimum, value)
    
    return None, minimum

def ida_star_search(state):
    search_statistics = { "expanded_paths": 0 }
    # at the start, bound has to be state.h, otherwise the entire tree would be pruned
    bound = state.h 
    init_state_key = create_state_key(state)

    while True:
        result, lowest_val = ida_star_bounded_search(state, 0, bound, {init_state_key}, search_statistics)

        if result is not None:
            return result, search_statistics["expanded_paths"]
        
        if lowest_val == float("inf"):
            return None, search_statistics["expanded_paths"]

        bound = lowest_val
    
    return

def q1_2_ida_star_driver(disks, pegs, heuristic, print_moves):
    State.heuristic_name = heuristic
    start_state = State.start_state(disks, pegs)
    solution, expanded_paths = ida_star_search(start_state)
    expected_val = (2 ** disks) - 1

    if print_moves:
        print_solution(start_state, solution)

    print(f"Expanded States: {expanded_paths}")
    print(f"Solution length ({disks}, {pegs}) = {len(solution)}")
    print(f"Expected value: 2^d - 1 = {expected_val}")

    if expected_val == len(solution):
        print("Expected value matches solution")
    else:
        print("Expected value does not match solution")

    return len(solution), expanded_paths

def q1_3c_ida_star_driver_h4a(disks, pegs, print_moves):
    State.heuristic_name = "h4a"
    start_state = State.start_state(disks, pegs)
    solution, expanded_paths = ida_star_search(start_state)

    if print_moves:
        print_solution(start_state, solution)
    
    print(f"f({disks},{pegs}) = {len(solution)}, expanded states = {expanded_paths}")
    return len(solution), expanded_paths
    
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--disks", type=int, default=4)
    arg_parser.add_argument("--pegs", type=int, default=3)
    arguments = arg_parser.parse_args()
    
    # 1.1
    # ids_driver_standard(arguments.disks, arguments.pegs, "old")

    # 1.2
    # for d in (4, 5):
    #     ida_star_driver(d, 3, "h3a", False)
    
    # for d in (4, 5, 6):
    #     ida_star_driver(d, 3, "h3b", True)

    # 1.3a
    # k_values = []
    # for d in range(7):
    #     length, _ = ids_driver_k(d, 4)
    #     k_values.append(length)
    #     print(k_values)

    # 1.3b
    for d in range(1, 8):
        ida_star_driver_4a(d, 4, False)

