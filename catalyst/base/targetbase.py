import os

from abc import ABC, abstractmethod
from pathlib import Path

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
        self.snapshot = None

    def set_snapshot(self, treeish=None):
        # Make snapshots directory
        snapshot_dir = Path(self.settings['storedir'], 'snapshots')
        snapshot_dir.mkdir(mode=0o755, parents=True, exist_ok=True)

        repo_name = self.settings['repo_name']
        if treeish is None:
            treeish = self.settings['snapshot_treeish']

        self.snapshot = Path(snapshot_dir,
                             f'{repo_name}-{treeish}.sqfs')

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
