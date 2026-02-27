"""
Autonomous Algorithmic Trading Researcher (AATR)
A system for autonomously generating, testing, and deploying trading algorithms.
"""

__version__ = "1.0.0"
__author__ = "Evolution Ecosystem AATR Team"

from aatr.state_manager import StateManager
from aatr.hypothesis_generator import HypothesisGenerator
from aatr.backtester import Backtester
from aatr.rl_agent import RLAgentTrainer
from aatr.deployment_manager import DeploymentManager

__all__ = [
    "StateManager",
    "HypothesisGenerator",
    "Backtester",
    "RLAgentTrainer",
    "DeploymentManager"
]