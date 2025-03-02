"""
Module defining the Trial class.
A Trial holds the decision variable values for one simulation run.
"""

from __future__ import annotations  # enable forward references
from typing import Any, Dict, List
from functools import lru_cache

# We import Variable from variable.py.
from .variable import Variable

class Trial:
    __slots__ = ["study", "trial_id", "variables", "_validated_variables"]

    def __init__(self, study: "SimulationStudyTabu", trial_id: int) -> None:
        self.study = study
        self.trial_id = trial_id
        self.variables: Dict[str, Any] = {}
        self._validated_variables = set()

    def __repr__(self) -> str:
        return f"Trial(trial_id={self.trial_id}, variables={self.variables})"

    @staticmethod
    @lru_cache(maxsize=None)
    def _validate_numerical_cached(name: str, low: float, high: float, expected_type: type, log: bool) -> None:
        if expected_type is float:
            if not (isinstance(low, (int, float)) and isinstance(high, (int, float))):
                raise TypeError(f"Variable '{name}': boundaries must be numeric.")
        elif expected_type is int:
            if not (isinstance(low, int) and isinstance(high, int)):
                raise TypeError(f"Variable '{name}': boundaries must be integers.")
        else:
            raise TypeError(f"Variable '{name}': Unsupported type {expected_type}.")
        low = expected_type(low)
        high = expected_type(high)
        if low >= high:
            raise ValueError(f"Variable '{name}': lower bound must be less than upper bound.")
        if log and (low <= 0 or high <= 0):
            raise ValueError(f"Variable '{name}': For logarithmic scale, boundaries must be positive.")

    def _validate_numerical(self, name: str, low: float, high: float, expected_type: type, log: bool) -> None:
        if not isinstance(name, str) or name == "":
            raise ValueError("Variable name must be a non-empty string.")
        self._validate_numerical_cached(name, low, high, expected_type, log)
        self._validated_variables.add(name)

    @staticmethod
    @lru_cache(maxsize=None)
    def _validate_categorical_cached(name: str, categories_tuple: tuple) -> None:
        if len(categories_tuple) < 1:
            raise ValueError(f"Variable '{name}': categories must contain at least one element.")
        if len(set(categories_tuple)) != len(categories_tuple):
            raise ValueError(f"Variable '{name}': categories contain duplicates.")

    def _validate_categorical(self, name: str, categories: List[str]) -> None:
        if not isinstance(name, str) or name == "":
            raise ValueError("Variable name must be a non-empty string.")
        if not isinstance(categories, list):
            raise TypeError(f"Variable '{name}': categories must be provided as a list.")
        if any(not isinstance(cat, str) for cat in categories):
            raise TypeError(f"Variable '{name}': all categories must be strings.")
        self._validate_categorical_cached(name, tuple(categories))
        self._validated_variables.add(name)

    def suggest_float(self, name: str, low: float, high: float, log: bool = False) -> float:
        self._validate_numerical(name, low, high, float, log)
        value = self.study._suggest_numerical(name, low, high, float, log)
        self.variables[name] = value
        return value

    def suggest_int(self, name: str, low: int, high: int, log: bool = False) -> int:
        self._validate_numerical(name, low, high, int, log)
        value = self.study._suggest_numerical(name, low, high, int, log)
        self.variables[name] = value
        return value

    def suggest_categorical(self, name: str, categories: List[str]) -> str:
        self._validate_categorical(name, categories)
        value = self.study._suggest_categorical(name, categories)
        self.variables[name] = value
        return value