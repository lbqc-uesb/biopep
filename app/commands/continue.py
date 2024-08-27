import os
import sys
from app.core import scraping


def execute(task_id: str):
    scraping.start(task_id)
    print("\nComplete molecular docking of peptides.")


if __name__ == "__main__":
    task_id = sys.argv[1]

    execute(task_id)
