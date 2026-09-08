from dataclasses import dataclass
from typing import Callable

import sqlite3


MigrationFunction = Callable[[sqlite3.Connection], None]


@dataclass(frozen=True)
class Migration:
    version: str
    upgrade: MigrationFunction

    def __post_init__(self):
        if not self.version.strip():
            raise ValueError("La version de migration ne peut pas etre vide.")

        if not callable(self.upgrade):
            raise TypeError("La migration doit fournir une fonction upgrade.")
