import json
import numpy as np
import time
import re
from pathlib import Path
import pandas as pd


def parse_bullets(sentence):
    bullets_preprocess = sentence.split("\n")
    bullets = []

    for bullet in bullets_preprocess:
        try:
            idx = bullet.find(next(filter(str.isalpha, bullet)))
        except:
            continue

        bullet = bullet[idx:]

        if len(bullet) != 0:
            bullets.append(bullet)

    return bullets


def parse_yes_no(string):
    """
    Parses a string containing "yes" or "no" and returns a boolean value.

    Args:
        string (str): The string to parse.

    Returns:
        bool: True if the string contains "yes", False if the string contains "no".

    Raises:
        ValueError: If the input string does not contain "yes" or "no".
    """
    if "yes" in string.lower():
        return True
    elif "no" in string.lower():
        return False
    else:
        return None


def solve_math_problems(input_str):
    pattern = r"\d+\.?\d*"

    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1]

    return None


def parse_answer(input_str):
    pattern = r"\((\w)\)"
    matches = re.findall(pattern, input_str)

    solution = None
    # print("predicted solution")
    # print(input_str)
    # print("matches")
    # print(matches)

    for match_str in matches[::-1]:
        solution = match_str.upper()
        if solution:
            break

    return solution


def compute_accuracy(gt, pred_solutions):
    if type(pred_solutions) == list:
        pred_answers = []

        for pred_solution in pred_solutions:
            pred_answer = parse_answer(pred_solution)

            if pred_answer is None:
                pred_answer = solve_math_problems(pred_solution)

            if pred_answer is not None:
                pred_answers.append(pred_answer)

        if pred_answer is None:
            return 0
        pred_answer = most_frequent(pred_answers)
        # pred_answer = pred_answers[0]
    else:
        pred_answer = parse_answer(pred_solutions)
        if pred_answer is None:
            pred_answer = solve_math_problems(pred_solutions)

    if gt == pred_answer:
        return 1
    else:
        return 0


def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        current_frequency = List.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num


if __name__ == "__main__":
    response_dict = json.load(open("mmlu_3_2.json", "r"))
    questions = list(response_dict.keys())

    accuracies = []
    accuracies_by_subject: dict[str, list[float]] = {}

    for question in questions:
        responses, gt, subject = response_dict[question]

        pred_solutions = []
        for response in responses:
            pred_solution = response[-1]["content"]

            pred_solutions.append(pred_solution)
            # break

        # pred_solutions = pred_solutions[:1]

        accurate = compute_accuracy(gt, pred_solutions)

        if accurate is not None:
            accuracies.append(float(accurate))
            accuracies_by_subject.setdefault(str(subject), []).append(float(accurate))
        else:
            import pdb

            pdb.set_trace()
            print(gt)

        print(
            "accuracies:",
            np.mean(accuracies),
            np.std(accuracies) / (len(accuracies) ** 0.5),
        )

    # Write per-subject accuracy report
    report_rows: list[dict[str, object]] = []
    for subject, subject_accuracies in accuracies_by_subject.items():
        n = len(subject_accuracies)
        mean_acc = float(np.mean(subject_accuracies)) if subject_accuracies else 0.0
        sem = float(np.std(subject_accuracies) / (n**0.5)) if n > 0 else 0.0
        report_rows.append(
            {
                "subject": subject,
                "n": n,
                "accuracy": mean_acc,
                "std_error": sem,
            }
        )

    report_path = Path("eval_by_subject.csv")
    report_dataframe = pd.DataFrame(
        report_rows, columns=["subject", "n", "accuracy", "std_error"]
    )
    report_dataframe.to_csv(report_path, index=False, encoding="utf-8")

    print(f"Wrote {report_path} (subjects={len(report_rows)})")
