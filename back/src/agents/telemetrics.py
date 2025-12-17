import csv
import time
from pathlib import Path
import os

file_path = Path("telemetrics.csv")

csv_header = ["timestamp", "model_kind", "model_name", "input_tokens", "output_tokens", "time_taken"]

def append_to_csv(model_kind: str, model_name: str, input_tokens: str, output_tokens :str, time_taken:float):
    data_row = [time.time(), model_kind, model_name, input_tokens, output_tokens, time_taken]
    if not file_path.exists():
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(csv_header)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data_row)

