import os
import glob
from abc import ABC, abstractmethod
from typing import Dict, Any

rules: Dict[str, Any] = {}
modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules]

class Rule(ABC):
    """
    One Rule for all, This Class is the masterClass and all rules 
    are gets inherited from this class

    Generic Rules Class: 
    All other rules should inherit from here, passing
    their **kwargs up to the super constructor.
    """
    def __init__(self, **kwargs: Any) -> None:
        self.action = kwargs.get('action')

    @abstractmethod
    def __call__(self, defnd_packet: Any) -> bool:
        """
        Return False to pass packet down the chain, "ACCEPT" to
        explicitly accept and "DROP" to explicitly drop.
        """
        pass

class SimpleRule(Rule):
    """
    Class for Simple Rules, it performs one action based on the 
    condition it meets, otherwise passes the action to other chain
    """
    def __call__(self, defnd_packet: Any) -> bool:
        if self.filter_condition(defnd_packet):
            return self.action
        else:
            return False

    @abstractmethod
    def filter_condition(self, defnd_packet: Any) -> bool:
        """
        Return True to perform default action, return False to pass packet
        down the chain. Override this to define correct behavior for your rule.
        """
        return True

def register(rule_class: Any) -> None:
    rules[rule_class.__name__] = rule_class
