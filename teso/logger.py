"""
Logging module for the optimization framework.
Provides a simple logger with a custom formatter and helper class.
"""

import logging
import sys
from typing import Optional

class SimpleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return f"[{self.formatTime(record, self.datefmt)}] {record.getMessage()}"

def setup_logger(name: str = "simopt", log_file: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers = []  # remove existing handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(SimpleFormatter(fmt="%(asctime)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(console_handler)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(SimpleFormatter(fmt="%(asctime)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(file_handler)
    return logger

class OptimizationLogger:
    def __init__(self, name: str = "simopt", log_file: Optional[str] = None):
        self.logger = setup_logger(name, log_file)

    def log_start(self, n_trials: int) -> None:
        self.logger.info(f"Optimization started with {n_trials} trials.")

    def log_trial(self, iteration: int, variables: dict, objective: float, objective_std: float,
                  best_iteration: int, best_value: float) -> None:
        var_str = ", ".join(f"{k}: {v:.3f}" if isinstance(v, float) else f"{k}: {v}" for k, v in variables.items())
        self.logger.info(
            f"Trial {iteration}: Obj={objective:.4f} (std={objective_std:.4f}); Vars: {{{var_str}}}; "
            f"Best: trial {best_iteration} ({best_value:.4f})."
        )