import os

from abc import ABC, abstractmethod

from catalyst.support import addl_arg_parse


class TargetBase(ABC):
    """
    The toplevel class for all targets. This is about as generic as we get.
    """

    def __init__(self, myspec, addlargs):
        addl_arg_parse(myspec, addlargs, self.required_values,
                       self.valid_values)
        self.settings = myspec
        self.env = {
            'PATH': '/bin:/sbin:/usr/bin:/usr/sbin',
            'TERM': os.getenv('TERM', 'dumb'),
        }

    @property
    @classmethod
    @abstractmethod
    def required_values(cls):
        return NotImplementedError

    @property
    @classmethod
    @abstractmethod
    def valid_values(cls):
        return NotImplementedError
