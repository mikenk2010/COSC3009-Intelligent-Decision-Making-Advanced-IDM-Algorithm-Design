from glob import glob
import pandas as pd
import json
import time
import random
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def construct_message(agents, question, idx):
    if len(agents) == 0:
        return {
            "role": "user",
            "content": "Can you double check that your answer is correct. Put your final answer in the form (X) at the end of your response.",
        }

    prefix_string = "These are the solutions to the problem from other agents: "

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\n One agent solution: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    prefix_string = (
        prefix_string
        + """\n\n Using the reasoning from other agents as additional advice, can you give an updated answer? Examine your solution and that other agents step by step. Put your answer in the form (X) at the end of your response.""".format(
            question
        )
    )
    return {"role": "user", "content": prefix_string}


def construct_assistant_message(completion):
    content = completion.choices[0].message.content
    return {"role": "assistant", "content": content}


def generate_answer(answer_context):
    try:
        completion = client.chat.completions.create(
            model="gpt-5-mini", messages=answer_context, n=1
        )
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)

    return completion


def parse_question_answer(df, ix):
    question = df.iloc[ix, 0]
    a = df.iloc[ix, 1]
    b = df.iloc[ix, 2]
    c = df.iloc[ix, 3]
    d = df.iloc[ix, 4]

    question = "Can you answer the following question as accurately as possible? {}: A) {}, B) {}, C) {}, D) {} Explain your answer, putting the answer in the form (X) at the end of your response.".format(
        question, a, b, c, d
    )

    answer = df.iloc[ix, 5]
    caterogy = df.iloc[ix, 6]
    return question, answer, caterogy

def construct_judge_message(question, agent_contexts, idx):
    prompt = """
You are an Olympiad-level mathematical judge.

Your role is to evaluate proposed solutions with the rigor of an International
Mathematical Olympiad jury.

You are not a solver.
You must not construct, extend, repair, or complete any solution.
You only verify correctness.

Judging principles:

1. Verification only  
Do not re-derive results, introduce new objects, or supply missing arguments.
If a required justification is missing, the solution is incorrect.

2. Object and assumption discipline  
Reject immediately if a solution introduces:
- objects not present in the problem,
- unstated assumptions,
- unjustified algebraic entities.

3. Logical validity  
Every nontrivial claim must be justified.
Invalid implications, misuse of theorems, or logical gaps are fatal errors.

4. Internal consistency  
Check for contradictions or false statements.
A single inconsistency is sufficient for rejection.

5. First-fatal-error rule (FFED)  
If a solution is incorrect, identify the first logically essential step where it fails.
Stop evaluation at that point.
Do not attempt to interpret intent or salvage correctness.

Judgment rules:

- If both solutions are fully correct and complete, state exactly:
  "CONSENSUS: Both solutions are correct."

- Otherwise, for each incorrect solution:
  - State REJECTED
  - Identify the first fatal error
  - Explain briefly why it is invalid
  - Do not provide a corrected solution

Output format:

Use the following sections only, in this exact order:

Evaluation of Agent A  
Evaluation of Agent B  
Overall Assessment  

Use concise, precise mathematical language.
Do not include rewritten proofs, new derivations, emojis,
or commentary outside the required sections.

Be strict.
Only accept solutions that would be accepted by an Olympiad jury.
"""
    prompt += f"Question:\n{question}\n\n"

    for i, agent in enumerate(agent_contexts):
        prompt += f"Agent {i} answer:\n```{agent[idx]['content']}```\n\n"

   

    return [{"role": "user", "content": prompt}]


def construct_revision_message(question, previous_answer, judge_feedback):
    return {
        "role": "user",
        "content": (
            f"Question:\n{question}\n\n"
            f"Your previous answer:\n{previous_answer}\n\n"
            f"Judge feedback:\n{judge_feedback}\n\n"
            "Revise your answer based ONLY on the judge feedback. "
            "Put your final answer in the form (X)."
        ),
    }

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    agents = 2
    rounds = 3

    df = pd.read_csv("mmlu_questions.csv")
    total_rows = len(df)
    if total_rows == 0:
        raise ValueError("mmlu_questions.csv is empty")

    random.seed(0)
    response_dict = {}
    counter = 0

    AGENT_PROMPT = """
You are {self.agent_id}, an Olympiad-level mathematician.

Your task is to solve the given problem correctly and rigorously.
Focus on mathematical validity, not verbosity.

General requirements:

1. Problem domain  
State the primary mathematical domain involved (e.g., algebra, number theory,
geometry, combinatorics). If more than one domain is involved, state this briefly.

2. Object discipline  
Only use objects explicitly given in the problem or those that follow directly
from standard definitions.
Do not introduce new elements, fields, constructions, or assumptions
unless they are logically forced.

3. Logical justification  
Every nontrivial claim must be justified.
You may be concise, but your reasoning must be correct.
Do not rely on pattern matching, counting arguments, or informal intuition
unless they are formally valid in this context.

4. Scope control  
Answer exactly what is asked.
Do not solve a different problem.
Do not introduce unnecessary generalizations.

5. Minimal generator and dependency check 
Explicitly state the minimal set of objects from the problem that are sufficient
to reach the final conclusion.
If any given objects are redundant or dependent on others, state this clearly.
Confirm that no additional objects were introduced.

Prohibitions:

- Do not invent new objects or generators
- Do not assume results without justification
- Do not use heuristic arguments as substitutes for logic
- Do not appeal to “standard facts” without indicating why they apply

Output format:

Use the following sections only:

Domain  
Clarification / Key Reasoning  
Minimal Generator Check  
Final Answer 

Use clear mathematical language.
All mathematical expressions must be written clearly in LaTeX.

Your solution should be short, correct, and complete.
"""

    for idx in range(total_rows):
        question, answer, subject = parse_question_answer(df, idx)

        # Initialize agent contexts (UNCHANGED)
        agent_contexts = [
            [{"role": "user", "content": question}] for _ in range(agents)
        ]

        # -----------------------------
        # Initial answers (round 0)
        # -----------------------------
        for i, agent_context in enumerate(agent_contexts):
            completion = generate_answer(agent_context)
            agent_context.append(construct_assistant_message(completion))

        # -----------------------------
        # Judge-mediated rounds
        # -----------------------------
        for round in range(1, rounds):
            # Judge evaluates all agents
            judge_context = construct_judge_message(
                question, agent_contexts, 2 * round - 1
            )
            judge_completion = generate_answer(judge_context)
            judge_feedback = judge_completion.choices[0].message.content

            # Agents revise ONLY from judge feedback
            for agent_context in agent_contexts:
                revision_message = construct_revision_message(
                    question,
                    agent_context[-1]["content"],
                    judge_feedback,
                )
                agent_context.append(revision_message)

                completion = generate_answer(agent_context)
                agent_context.append(construct_assistant_message(completion))

        response_dict[question] = (agent_contexts, answer, subject)
        print(counter)
        counter += 1

    json.dump(
        response_dict,
        open(f"mmlu_{agents}_{rounds}.json", "w"),
    )