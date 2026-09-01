# Prompt Lab

## Overview

This project compares four prompting strategies for extracting
structured information from job descriptions using an LLM.

The four strategies are:

- Zero-shot
- Few-shot
- Structured/Role-based
- Chain-of-Thought (CoT)

Each strategy extracts:

- Company
- Role
- Years of experience required

from the same set of job snippets.

## Project Structure

```text
MP1_Prompt_Lab/
├── calls.py
├── prompts.py
├── settings.py
├── requirements.txt
├── data/
└── results.json

## Run
python calls.py

## Results
Based on the data in mp1_comparison.md, Few-shot prompting was the strongest overall strategy in this experiment. Zero-shot had the lowest candidate cost, while all four strategies achieved a 100% parse rate.

## Future Improvements
- Test with a larger dataset
- Try other prompting strategies
- Try other LLM
