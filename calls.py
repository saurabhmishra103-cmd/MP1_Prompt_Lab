import asyncio
import time
import json
import statistics

from data.data import snippets, golden
from prompts import prompt_zero_shot, client, STRATEGIES
from settings import CANDIDATE_MODEL, JUDGE_MODEL, RATES

def calculate_accuracy(llm_response, expected):
    score = 0
    if str(llm_response.get("company","")).strip().lower() == str(expected.get("company","")).strip().lower():
        score += 1
    if str(llm_response.get("role","")).strip().lower() == str(expected.get("role","")).strip().lower():
        score += 1
    if str(llm_response.get("years_experience_required","")).strip().lower() == str(expected.get("years_experience_required","")).strip().lower():
        score += 1

    return score



async def llm_judge(snippet_text, golden_answer, candidate_answer):
    judge_prompt = f"""
    Evaluate the candidate answer against the expected answer.
    Job posting: {snippet_text},
    Expected answer: {json.dumps(golden_answer)}
    Candidate answer: {json.dumps(candidate_answer)}

    give a score from 1 to 4 based on how well 
    the candidate answer matches with the expected answer
    in line with the following:
    -- 4 = fully correct given the details
    -- 3 = mostly correct, minor issues
    -- 2 = partially correct, significant issues
    -- 1 = incorrect or misleading

    Return ONLY:
    {{
        "score" : integer
    }}
    """

    response = await client.chat.completions.create(
        model = JUDGE_MODEL,
        messages = [
            {"role" : "system", "content" : "You are an evaluator of extracted results. return the evaluation as JSON"},
            {"role" : "user", "content" : judge_prompt}
        ],
        response_format = {"type" : "json_object"},
        temperature = 0.0
    )
    raw_judge_response = response.choices[0].message.content
    return json.loads(raw_judge_response)

    
async def evaluate_one(snippet, strategy_name):
    strategy_function = STRATEGIES[strategy_name]
    start_time = time.perf_counter()
    result = await strategy_function(snippet["snippet"])
    end_time = time.perf_counter()
    time_taken = end_time - start_time      #LATENCY

# GOLDEN ANSWER
    golden_answer = golden[snippet["id"]]

# ACCURACY
    if result["parse_success"]:
        accuracy = calculate_accuracy(result["parsed_response"], golden_answer)
    else:
        accuracy = 0
    
# COST
    usage = result["usage"]

    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens

    cost = (
        input_tokens * RATES[CANDIDATE_MODEL]["in"] 
        + output_tokens * RATES[CANDIDATE_MODEL]["out"]
        )

# llm_judge
    judge_result = await llm_judge(
        snippet["snippet"], 
        golden_answer, 
        result["parsed_response"]
        )

    return {
        "snippet_id": snippet["id"],
        "strategy": strategy_name,
        "raw_response": result["raw_response"],
        "parsed_response": result["parsed_response"],
        "parse_success": result["parse_success"],
        "accuracy": accuracy,
        "judge_score": judge_result["score"],
        "cost": cost,
        "latency": time_taken
    }


async def main():
    tasks = []

    for snippet in snippets:
        for strategy_name in STRATEGIES:
            tasks.append(
                evaluate_one(snippet, strategy_name)
            )

    results = await asyncio.gather(*tasks)

    print(f"Completed {len(results)} evaluations")

    for result in results:
        print(result)

    return results


# All calls and get results
results = asyncio.run(main())
print(f"\nTotal results collected: {len(results)}")

# Save the results
with open("results.json","w", encoding="utf-8") as file:
    json.dump(results, file, indent=4, default=str)
print("\n40 results saved to results.json")

# group results by strategy
results_by_strategy = {}
for result in results:
    strategy = result["strategy"]
    if strategy not in results_by_strategy:
        results_by_strategy[strategy] = []
    results_by_strategy[strategy].append(result)

print("\nResults grouped by strategy: ")
for strategy, strategy_results in results_by_strategy.items():
    print(f"{strategy}: {len(strategy_results)} results")

#CALUCLATE SUMMARY METRICS
summary_results = []

for strategy, strategy_results in results_by_strategy.items():
    #Parse Rate
    successful_parse = sum(
        result["parse_success"]
        for result in strategy_results
    )

    parse_rate = (successful_parse/len(strategy_results))*100

    #Accuracy Mean
    accuracy_mean = statistics.mean(
        result["accuracy"]
        for result in strategy_results
    )

    # Mean LLM Judge Score
    judge_score_mean = statistics.mean(
        result["judge_score"]
        for result in strategy_results
    )

    # Total Candidate Cost
    total_cost = sum(
        result["cost"]
        for result in strategy_results
    )

    # P50 Latency
    p50_latency = statistics.median(
        result["latency"]
        for result in strategy_results
    )

    #Store Summary
    summary_results.append({
        "strategy": strategy,
        "accuracy_mean": accuracy_mean,
        "parse_rate": parse_rate,
        "mean_judge_score": judge_score_mean,
        "total_cost": total_cost,
        "p50_latency": p50_latency
    })

#Comparison Table
print("\n" + "=" * 90)
print("PROMPT STRATEGY COMPARISON")
print("=" * 90)

print(
    f"{'Strategy':<15}"
    f"{'Accuracy':<15}"
    f"{'Parse Rate':<15}"
    f"{'Judge Score':<15}"
    f"{'Total Cost':<15}"
    f"{'P50 Latency':<15}"
)

print("-" * 90)

for summary in summary_results:

    print(
        f"{summary['strategy']:<15}"
        f"{summary['accuracy_mean']:.1f}/3"
        f"{'':<10}"
        f"{summary['parse_rate']:.1f}%"
        f"{'':<9}"
        f"{summary['mean_judge_score']:.2f}"
        f"{'':<10}"
        f"${summary['total_cost']:.6f}"
        f"{'':<6}"
        f"{summary['p50_latency']:.2f}s"
    )

print("=" * 90)