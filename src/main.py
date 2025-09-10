#!/usr/bin/env python
import sys
import warnings
import os

from datetime import datetime
from pathlib import Path

from src.research_daad.crew import ResearchDaad
import src.utils.config as CONFIG
# from dotenv import load_dotenv


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        researchDaad = ResearchDaad()
        result = researchDaad.crew().kickoff()
        # result = ResearchDaad().crew().kickoff(inputs=inputs)

        # Split markdown and CSV content
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)

        if '[CSV]' in result and '[MARKDOWN]' in result:
            md_content = result.split('[MARKDOWN]')[1].split('[CSV]')[0].strip()
            csv_content = result.split('[CSV]')[1].strip()

            with open(f'{out_dir}/scholarships.md', 'w') as md_file:
                md_file.write(md_content)

            with open(f'{out_dir}/scholarships.csv', 'w') as csv_file:
                csv_file.write(csv_content)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        ResearchDaad().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ResearchDaad().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        ResearchDaad().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    run()
