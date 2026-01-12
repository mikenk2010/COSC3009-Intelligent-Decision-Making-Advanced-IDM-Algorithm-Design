from __future__ import annotations

import hashlib
from pathlib import Path
import random
from typing import Any

import csv
import numpy as np
import pandas as pd
from datasets import load_dataset


# Configuration
QUESTIONS_PER_SUBJECT = 3  # Change this to get more questions per subject


def _stable_int_from_text(text: str) -> int:
    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _as_choice_list(choices_value: Any) -> list[str]:
    if choices_value is None:
        return []

    if isinstance(choices_value, (list, tuple, np.ndarray)):
        return [str(item) for item in list(choices_value)]

    return [str(choices_value)]


def _answer_to_letter(answer_value: Any) -> str | None:
    index_to_letter = {0: "A", 1: "B", 2: "C", 3: "D"}

    if answer_value is None or (
        isinstance(answer_value, float) and np.isnan(answer_value)
    ):
        return None

    if isinstance(answer_value, (int, np.integer)):
        return index_to_letter.get(int(answer_value), str(int(answer_value)))

    answer_string = str(answer_value).strip().upper()
    if answer_string in {"A", "B", "C", "D"}:
        return answer_string

    if answer_string.isdigit():
        return index_to_letter.get(int(answer_string), answer_string)

    return answer_string


def main() -> None:
    # Load dataset from Hugging Face
    print("Loading MMLU dataset from Hugging Face...")
    dataset = load_dataset("cais/mmlu", "all", split="test")
    dataframe = dataset.to_pandas()
    print(f"Loaded {len(dataframe)} rows from MMLU dataset")

    # Match the CSV layout that `gen_mmlu.py` expects.
    output_csv_path = Path(__file__).with_name("mmlu_questions.csv")
    delimiter = ","
    random_seed = int(random.randint(0, 2**32))

    flattened_rows: list[dict[str, Any]] = []
    for _, row in dataframe.iterrows():
        choices_list = _as_choice_list(row.get("choices"))
        flattened_rows.append(
            {
                "question": row.get("question"),
                "A": choices_list[0] if len(choices_list) > 0 else None,
                "B": choices_list[1] if len(choices_list) > 1 else None,
                "C": choices_list[2] if len(choices_list) > 2 else None,
                "D": choices_list[3] if len(choices_list) > 3 else None,
                "answer": _answer_to_letter(row.get("answer")),
                "subject": row.get("subject"),
            }
        )

    output_dataframe = pd.DataFrame(flattened_rows)[
        ["question", "A", "B", "C", "D", "answer", "subject"]
    ]

    sampled_frames: list[pd.DataFrame] = []
    for subject, group in output_dataframe.groupby("subject", sort=True):
        per_subject_seed = (int(random_seed) + _stable_int_from_text(str(subject))) % (
            2**32
        )
        # Don't exceed available questions
        n_samples = min(QUESTIONS_PER_SUBJECT, len(group))
        sampled_frames.append(group.sample(n=n_samples, random_state=per_subject_seed))

    sampled_dataframe = pd.concat(sampled_frames, ignore_index=True)
    sampled_dataframe.to_csv(
        output_csv_path,
        index=False,
        encoding="utf-8",
        sep=delimiter,
        lineterminator="\n",
        quoting=csv.QUOTE_ALL,
    )

    print(
        "Wrote",
        str(output_csv_path.resolve()),
        f"({len(sampled_dataframe)} rows, {sampled_dataframe['subject'].nunique()} subjects)",
        "from Hugging Face dataset cais/mmlu",
    )


if __name__ == "__main__":
    main()
