from typing import List, Dict, Optional

from block import Block
from config import Configuration


class Generator:
    def __init__(self, configuration: Optional[Configuration] = None):
        self.configuration: Configuration = configuration
        self._generated: Dict[int, List[Block]] = {}
        self.__hash = hash(configuration)

    def _generate(self, x: int):
        raise NotImplementedError

    def __call__(self, x: int) -> List[Block]:
        if hash(self.configuration) != self.__hash:
            self._generated = {}
        if x not in self._generated:
            self._generate(x)
        return self._generated[x]
