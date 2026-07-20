from typing import Protocol
import pandas as pd

class ParserProtocol(Protocol):
    def parse(self, path: str) -> pd.DataFrame:
        ...
