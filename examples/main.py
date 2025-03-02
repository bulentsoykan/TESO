"""
Example main.py file to solve the MM1 queue simulation‐optimization problem using TESO.
"""

from teso.simulation_study_tabu import SimulationStudyTabu

#!/usr/bin/env python
"""
Main file to solve the M/M/1 queue simulation‐optimization problem using the
Tabu‐Enhanced Simulation Optimization (TESO) algorithm. The objective is to find
a service rate, “mu”, that minimizes the average sojourn time plus a cost penalty.
"""

import numpy as np
from mrg32k3a.mrg32k3a import MRG32k3a
from mm1queue import MM1MinMeanSojournTime, MM1Queue

# Global variable to hold the problem instance.
problem = None

def simulate_mm1(mu_value: float, model_factors: dict) -> dict:
    """
    Runs a single replication of the MM1 queue simulation model using a given service rate.
    
    Arguments:
        mu_value: The candidate service rate.
        model_factors: A dictionary of model parameters (including lambda, warmup, etc.).

    Returns:
        responses: A dictionary of performance measures from the simulation replication.
    """
    # Update model factors with the candidate service rate.
    factors = model_factors.copy()
    factors["mu"] = mu_value
    # Instantiate the MM1 queue model with these factors.
    mm1_model = MM1Queue(fixed_factors=factors)
    
    # Provide a seed sequence (6 integers) to the RNG constructors.
    rng1_seed = (123456, 234567, 345678, 456789, 567890, 678901)
    rng2_seed = (654321, 765432, 876543, 987654, 198765, 219876)
    rng1 = MRG32k3a(rng1_seed)
    rng2 = MRG32k3a(rng2_seed)
    
    responses, gradients = mm1_model.replicate([rng1, rng2])
    return responses

def objective_function(trial) -> float:
    """
    Objective function for simulation optimization.
    
    It uses the trial to suggest a candidate value for the decision variable 'mu',
    runs the MM1 simulation to measure average sojourn time, and returns the overall
    objective, which is:
      
         objective = avg_sojourn_time + cost * (mu^2)
      
    where cost is obtained from the problem factors.
    """
    # Suggest a candidate service rate for the MM1 queue.
    mu_candidate = trial.suggest_float("mu", 0.1, 10.0, log=False)
    
    # Retrieve the cost factor (default is 0.1) from the problem.
    cost = problem.factors.get("cost", 0.1)
    
    # Assemble model factors—using defaults from the problem for parameters like warmup and people.
    model_factors = problem.model_default_factors.copy()
    model_factors["lambda"] = 1.5      # Interarrival rate (example value)
    model_factors["epsilon"] = 0.001     # Ensure service rate mu is at least epsilon
    
    # Run one replication of the MM1 simulation.
    responses = simulate_mm1(mu_candidate, model_factors)
    avg_sojourn = responses["avg_sojourn_time"]
    
    # Combine simulation response with a quadratic penalty in mu.
    objective_value = avg_sojourn + cost * (mu_candidate ** 2)
    return objective_value

def main():
    global problem
    # Create an instance of the MM1MinMeanSojournTime problem.
    problem = MM1MinMeanSojournTime(
        name="MM1-Queue-MinMeanSojournTime",
        fixed_factors={"cost": 0.1},
        model_fixed_factors={}
    )
    
    print("Starting simulation optimization for the M/M/1 queue problem...")
    
    # Create an optimizer using the Tabu‐Enhanced Simulation Optimization (TESO) strategy.
    optimizer = SimulationStudyTabu(
        direction="minimize",
        n_init_points=5,
        initial_noise=0.5,
        final_noise=0.05,
        random_state=42,
        verbose=True,
        n_replications=5,
        max_no_improve=10
    )
    
    # Run the optimization for a specified number of trials.
    optimizer.optimize(objective_function, n_trials=50)
    
    # Retrieve and print the best candidate solution (i.e. the 'mu' value).
    best_candidate = optimizer.elite_memory.get_best()
    print("\nBest candidate (model decision factors):", best_candidate)
    print("Best objective value achieved:", optimizer.best_objective_value)

if __name__ == "__main__":
    main()
