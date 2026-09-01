
## 1. Which strategy won, and on what dimension? (Accuracy?
Parse rate? Cost?):
- **Accuracy**:   few_shot
- **Parse Rate**: all same. I am constraining the model to return JSON only. Therefore, I would expect the parse rates to be 100% for all strategies
- **Cost**:       zero_shot

## 2. What surprised you? Either a strategy worked better than expected, or worse, or a specific snippet failed in a way you didn't predict.
### 2.1. Few-shot performance:
Few-shot prompt had the highest accuracy with the lowest latency, that seems contrary to the general understanding that better accuracy might need more time to process.
### 2.2. Chain-of-Thought performance:
Surprised to see that the Chain-of-Thought strategy was not the best in accuracy
### 2.3. j07 result:
For **j07**, the requirement was of Engineering Manager with "three years leading engineering teams, plus a solid IC background before that" and each strategy returned "years_experience_required" as 3, which is correct considering the numbers, but logically it is incorrect, because it also asks for IC background before that.
### 2.4. Number of LLM Calls:
The project mentions 40 LLM calls. However, there are 40 additional calls to judge LLM which means a **total of 80 calls**. This also means the cost shown in the comparison table is only for Candidate LLM and not Judge LLM.


## 3. For *your* capstone domain, which strategy would you reach
for first? Justify in 2-3 sentences.
I would prefer to use the **few-shot** strategy. This is because my foremost consideration would be giving the correct output to the user. The latency is also the lowest for few-shot prompting amongst the strategies. 

## 4. If you had another day, what would you try next? (Different
model? More snippets? Different prompts?):
I would try **more snippets**. This should give me a better insight into the data received from LLM, as currently the dataset is very small.