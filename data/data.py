from pathlib import Path
import json
DATA_DIR = Path(r"C:\Users\saura\AIRAG-Capstone-Project\MP1\MP1_Prompt_Lab\data\uploads")   # adjust if your folder layout differs

snippets = [json.loads(line) 
            for line in (DATA_DIR / 'jobs_snippets.jsonl').read_text().splitlines() 
            if line.strip()
            ]
golden = {
    row['id']: row 
    for row in (
        json.loads(line)
        for line in (DATA_DIR / 'golden_set.jsonl').read_text().splitlines() 
        if line.strip()
        )
        }