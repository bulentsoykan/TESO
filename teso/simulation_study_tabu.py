"""
The SimulationStudyTabu class implements a simulation optimization 
framework using tabu search and memory strategies (elite memory).
"""

import numpy as np
from numpy.typing import NDArray
from time import perf_counter
from typing import Callable, Union, Optional, Dict, Any

from .logger import OptimizationLogger
from .memory import TabuList, EliteMemory
from .trial import Trial
from .variable import Variable

class SimulationStudyTabu:
    def __init__(
        self,
        direction: str = "minimize",
        n_init_points: Optional[int] = None,
        initial_noise: float = 0.2,
        final_noise: Optional[float] = None,
        random_state: Optional[int] = None,
        verbose: bool = True,
        n_replications: int = 30,
        max_no_improve: Optional[int] = 20
    ) -> None:
        self.direction = direction
        self.n_init_points = n_init_points if n_init_points is not None else 10
        self.initial_noise = initial_noise
        self.final_noise = final_noise if final_noise is not None else 0.05
        self.n_replications = n_replications
        self.max_no_improve = max_no_improve
        self.verbose = verbose

        self.best_objective_value = float('inf') if direction == "minimize" else float('-inf')
        self.trials_without_improvement = 0

        self._rng = np.random.RandomState(random_state)
        self.n_trials = None  # to be set in optimize()

        self._objective_values: Optional[NDArray[np.float64]] = None
        self._objective_stds: Optional[NDArray[np.float64]] = None
        self._elapsed_times: Optional[NDArray[np.float64]] = None

        self._current_trial: Optional[Trial] = None
        self._variables: Dict[str, Variable] = {}

        self._current_noise = self.initial_noise
        self._logger = OptimizationLogger() if verbose else None

        # New memory structures
        self.tabu_list = TabuList(max_size=20)
        self.elite_memory = EliteMemory(capacity=10)
        self.max_candidate_attempts = 10

    def _candidate_representation(self, trial: Trial) -> tuple:
        # Convert trial variables into a sorted tuple (hashable representation).
        return tuple(sorted(trial.variables.items()))

    def _suggest_numerical(self, name: str, low: Union[int, float], high: Union[int, float],
                           var_type: type, log: bool) -> Union[float, int]:
        if name not in self._variables:
            var = Variable(name)
            var.set_values(max_iter=self.n_trials, var_type_or_categories=var_type)
            self._variables[name] = var
        else:
            var = self._variables[name]
            if var.type != var_type:
                raise TypeError(f"Variable {name} already set to type {var.type} not {var_type}.")

        if self._current_trial.trial_id < self.n_init_points:
            # Pure random sampling.
            if log:
                return np.exp(self._rng.uniform(np.log(low), np.log(high)))
            else:
                return self._rng.uniform(low, high)
        else:
            # Exploitation: try using an elite value.
            elite_value = None
            best_candidate = self.elite_memory.get_best()
            if best_candidate is not None and name in best_candidate:
                elite_value = best_candidate[name]
            if elite_value is None or self._rng.rand() < 0.5:
                base_value = self._rng.uniform(low, high)
            else:
                base_value = elite_value
            var_range = high - low
            noise = self._rng.normal(loc=0.0, scale=self._current_noise * var_range)
            value = base_value + noise
            return self._reflect_at_boundaries(value, low, high)

    def _suggest_categorical(self, name: str, categories: list) -> Any:
        if name not in self._variables:
            var = Variable(name)
            var.set_values(max_iter=self.n_trials, var_type_or_categories=categories)
            self._variables[name] = var
        else:
            var = self._variables[name]
            if var.type is not list:
                raise TypeError(f"Variable {name} is not categorical.")
            var.set_values(max_iter=self.n_trials, var_type_or_categories=categories)
        if self._current_trial.trial_id < self.n_init_points or self.elite_memory.get_best() is None:
            chosen_category = self._rng.choice(categories)
        else:
            best_candidate = self.elite_memory.get_best()
            base_category = best_candidate.get(name, self._rng.choice(categories))
            if self._rng.rand() < 0.3:
                chosen_category = self._rng.choice(categories)
            else:
                chosen_category = base_category
        return chosen_category

    @staticmethod
    def _reflect_at_boundaries(x: float, low: float, high: float) -> float:
        while x < low or x > high:
            if x < low:
                x = low + (low - x)
            if x > high:
                x = high - (x - high)
        return x

    def optimize(self, objective_function: Callable[[Trial], Union[float, int]], n_trials: int) -> None:
        if n_trials <= 0:
            raise ValueError("n_trials must be a positive integer.")
        self.n_trials = n_trials
        self._objective_values = np.empty(n_trials, dtype=np.float64)
        self._objective_stds = np.empty(n_trials, dtype=np.float64)
        self._elapsed_times = np.empty(n_trials, dtype=np.float64)

        if self.verbose:
            self._logger.log_start(n_trials)

        for iteration in range(n_trials):
            candidate_found = False
            attempt = 0
            while not candidate_found and attempt < self.max_candidate_attempts:
                if iteration < self.n_init_points or self._rng.rand() < 0.3:
                    # Diversification: generate a candidate at random.
                    self._current_trial = Trial(self, iteration)
                    objective_function(self._current_trial)
                else:
                    # Intensification: perturb an elite candidate.
                    elite_candidate = self.elite_memory.get_best()
                    self._current_trial = Trial(self, iteration)
                    if elite_candidate is not None:
                        self._current_trial.variables = elite_candidate.copy()
                        for var_name, value in elite_candidate.items():
                            if isinstance(value, (int, float)):
                                perturb = self._rng.normal(0, self._current_noise * (abs(value) + 1e-3))
                                # Example with fixed bounds (e.g., 0 to 10); in a full code you’d store bounds per variable.
                                self._current_trial.variables[var_name] = self._reflect_at_boundaries(value + perturb, 0.0, 10.0)
                            else:
                                if self._rng.rand() < 0.3:
                                    self._current_trial.variables[var_name] = value
                    else:
                        # Fallback if no elite candidate.
                        objective_function(Trial(self, iteration))
                candidate_key = self._candidate_representation(self._current_trial)
                if self.tabu_list.is_tabu(candidate_key):
                    # Aspirational criteria.
                    candidate_obj = objective_function(self._current_trial)
                    if (self.direction == "minimize" and candidate_obj < self.best_objective_value) or \
                       (self.direction == "maximize" and candidate_obj > self.best_objective_value):
                        candidate_found = True
                    else:
                        attempt += 1
                        continue
                else:
                    candidate_found = True

            start_time = perf_counter()
            rep_results = [objective_function(self._current_trial) for _ in range(self.n_replications)]
            rep_results = np.array(rep_results)
            obj_mean = rep_results.mean()
            obj_std = rep_results.std()
            elapsed = perf_counter() - start_time

            self._objective_values[iteration] = obj_mean
            self._objective_stds[iteration] = obj_std
            self._elapsed_times[iteration] = elapsed

            if (self.direction == "minimize" and obj_mean < self.best_objective_value) or \
               (self.direction == "maximize" and obj_mean > self.best_objective_value):
                self.best_objective_value = obj_mean
                self.trials_without_improvement = 0
            else:
                self.trials_without_improvement += 1

            # Update memory structures.
            cid = self._candidate_representation(self._current_trial)
            self.tabu_list.add(cid)
            self.elite_memory.add(self._current_trial.variables, obj_mean, direction=self.direction)

            if self.verbose:
                self._logger.log_trial(iteration + 1, self._current_trial.variables,
                                        obj_mean, obj_std, iteration + 1, self.best_objective_value)

            if self.max_no_improve is not None and self.trials_without_improvement >= self.max_no_improve:
                if self.verbose:
                    self._logger.logger.info(f"Stopping optimization: No improvement for {self.max_no_improve} trials.")
                break