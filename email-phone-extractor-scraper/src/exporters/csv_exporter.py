import csv
from typing import List, Dict

class CSVExporter:
    def __init__(self, output_path: str, field_order: List[str]):
        self.output_path = output_path
        self.field_order = field_order

    def export(self, records: List[Dict]) -> None:
        with open(self.output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.field_order, extrasaction="ignore")
            writer.writeheader()
            for r in records:
                writer.writerow({k: (r.get(k) or "") for k in self.field_order})