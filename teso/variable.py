"""
Classes for decision variables.
  • CategoryIndexer: handles mapping between category names and indices.
  • Variable: represents a decision variable (continuous or categorical) with
    storage for the candidate values over iterations.
"""

from typing import List, Union
import numpy as np
from numpy.typing import NDArray

class CategoryIndexer:
    def __init__(self) -> None:
        self.str_to_idx = {}  # maps string to index
        self.idx_to_str = {}  # maps index to string
        self.next_idx = 0

    def get_indices(self, strings: List[str]) -> NDArray:
        indices = np.empty(len(strings), dtype=np.int32)
        for i, cat in enumerate(strings):
            if cat not in self.str_to_idx:
                self.str_to_idx[cat] = self.next_idx
                self.idx_to_str[self.next_idx] = cat
                self.next_idx += 1
            indices[i] = self.str_to_idx[cat]
        return indices

    def get_strings(self, indice: int) -> str:
        return self.idx_to_str[indice]


class Variable:
    def __init__(self, name: str):
        self.name = name
        self.type = None  # will be set to int, float, or list (for categorical)
        self.values = None  # will hold candidate values over iterations
        self.category_indexer = CategoryIndexer()

    def set_values(self, max_iter: int, var_type_or_categories: Union[type, List[str]]) -> None:
        if isinstance(var_type_or_categories, type):
            # Continuous variable: initialize with NaN values
            self.values = np.full(max_iter, np.nan, dtype=np.float64)
            self.type = var_type_or_categories
        elif isinstance(var_type_or_categories, list):
            # Categorical variable: create a binary encoded array per candidate.
            categories = var_type_or_categories
            if not categories:
                raise ValueError("Categories list cannot be empty.")
            cat_indices = self.category_indexer.get_indices(categories)
            required_width = int(cat_indices.max()) + 1
            self.values = np.zeros((max_iter, required_width), dtype=np.float64)
            self.type = list  # for categorical variables
        else:
            raise TypeError("var_type_or_categories must be a type or list of strings.")

    def add_iter(self, additional_iter: int) -> None:
        if additional_iter <= 0:
            raise ValueError("additional_iter must be greater than zero.")
        if self.values is None:
            raise ValueError("Values array has not been initialized.")
        if self.values.ndim == 1:
            extension = np.full(additional_iter, np.nan, dtype=self.values.dtype)
            self.values = np.concatenate((self.values, extension))
        else:
            extension = np.zeros((additional_iter, self.values.shape[1]), dtype=self.values.dtype)
            self.values = np.vstack((self.values, extension))