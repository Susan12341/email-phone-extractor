import json
from typing import List, Dict

class JSONExporter:
    def __init__(self, output_path: str, indent: int = 2):
        self.output_path = output_path
        self.indent = indent

    def export(self, records: List[Dict]) -> None:
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=self.indent, ensure_ascii=False)