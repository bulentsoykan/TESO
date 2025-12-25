---
title: 'TESO: A Python Package for Tabu-Enhanced Simulation Optimization'
tags:
  - Python
  - simulation optimization
  - tabu search
  - metaheuristics
  - stochastic optimization
authors:
  - name: Bulent Soykan
    orcid: 0000-0002-7958-2650
    affiliation: 1
affiliations:
  - name: Research Scientist, United States
    index: 1
date: 25 December 2025
bibliography: paper.bib
---

# Summary

TESO (Tabu-Enhanced Simulation Optimization) is a Python package that implements a metaheuristic optimization algorithm combining tabu search with adaptive memory strategies for solving simulation optimization problems. The algorithm is designed to efficiently optimize objective functions that are expensive to evaluate and subject to stochastic noise, which is common in simulation-based studies.

TESO integrates three core mechanisms: (1) diversification through random sampling to explore the solution space broadly, (2) intensification via guided local search around elite solutions stored in memory, and (3) a tabu list with aspiration criteria to prevent cycling while allowing promising moves. The package supports continuous, discrete, and categorical decision variables, making it applicable to a wide range of simulation optimization problems.

# Statement of Need

Simulation optimization is a critical methodology in operations research, manufacturing, healthcare, and logistics, where analytical solutions are often intractable and system behavior must be evaluated through simulation [@fu2002optimization]. The challenge lies in optimizing objectives that are noisy (due to stochastic simulation outputs) and expensive to evaluate (due to computational cost of running simulations).

While derivative-free optimization methods exist, many struggle with the noise inherent in simulation outputs or require excessive function evaluations. Tabu search [@glover1989tabu; @glover1990tabu] has proven effective for combinatorial optimization, but implementations tailored for simulation optimization with continuous variables and noisy evaluations are limited.

TESO addresses this gap by providing a Python implementation specifically designed for simulation optimization contexts. Unlike general-purpose optimizers, TESO incorporates:

- **Noise-aware evaluation**: Multiple replications per solution to obtain reliable performance estimates
- **Adaptive perturbation**: Dynamic adjustment of search step sizes to balance exploration and exploitation
- **Elite memory**: Storage and exploitation of high-performing solutions discovered during search
- **Flexible variable handling**: Native support for mixed continuous, discrete, and categorical variables

The package integrates seamlessly with existing Python simulation frameworks and follows a familiar API pattern inspired by Optuna [@akiba2019optuna], lowering the barrier to adoption. Researchers and practitioners can define their simulation models as objective functions and leverage TESO's optimization capabilities with minimal setup.

TESO has been applied to classical queueing system optimization problems (e.g., M/M/1 queues) and is suitable for broader applications including inventory management, service system design, and manufacturing process optimization. The package was presented at the Winter Simulation Conference 2025 [@soykan2025teso].

# References
