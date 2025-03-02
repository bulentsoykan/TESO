"""
Memory structures for the optimization framework:
  • TabuList – stores recently visited (taboo) candidates.
  • EliteMemory – stores the best (elite) candidates so far.
"""

from typing import Tuple, Optional, Dict, Any

class TabuList:
    def __init__(self, max_size: int = 20) -> None:
        self.tabu_items = []  # list of candidate representations (tuples)
        self.max_size = max_size

    def add(self, candidate: tuple) -> None:
        self.tabu_items.append(candidate)
        if len(self.tabu_items) > self.max_size:
            self.tabu_items.pop(0)

    def is_tabu(self, candidate: tuple) -> bool:
        return candidate in self.tabu_items


class EliteMemory:
    def __init__(self, capacity: int = 10) -> None:
        self.capacity = capacity
        # Each entry: (candidate, objective_value)
        self.elite_solutions = []  # type: list[tuple[Dict[str, Any], float]]

    def add(self, candidate: Dict[str, Any], obj_val: float, direction: str = "minimize") -> None:
        candidate_tuple = self._to_tuple(candidate)
        # Skip if already stored.
        if any(candidate_tuple == self._to_tuple(cand) for cand, _ in self.elite_solutions):
            return

        self.elite_solutions.append((candidate, obj_val))
        if direction == "minimize":
            self.elite_solutions.sort(key=lambda x: x[1])
        else:
            self.elite_solutions.sort(key=lambda x: -x[1])
        if len(self.elite_solutions) > self.capacity:
            self.elite_solutions.pop()  # remove the worst among the elite

    def get_best(self) -> Optional[Dict[str, Any]]:
        if self.elite_solutions:
            return self.elite_solutions[0][0]
        return None

    def _to_tuple(self, candidate: Dict[str, Any]) -> tuple:
        # Convert candidate dict into an ordered (sorted) tuple representation.
        return tuple(sorted(candidate.items()))