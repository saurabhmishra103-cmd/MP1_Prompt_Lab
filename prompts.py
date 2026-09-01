from openai import AsyncOpenAI
from settings import my_settings, CANDIDATE_MODEL, JUDGE_MODEL
import os 
import json
from data.data import snippets, golden

client = AsyncOpenAI(
    api_key=my_settings.OPENAI_API_KEY,
    base_url=my_settings.OPENAI_BASE_URL
)

async def prompt_zero_shot(snippet_text: str) -> list[dict]:
    """Strategy 1 — zero-shot. Just ask, no examples, no persona.
        Takes a natural language string and extracts transaction data using OpenAI.
        """
    
    system_instruction = """
        TASK: Extract:
            - "company".
            - "role".
            - "years_experience_required".
        FORMAT: Return JSON.
        """
    
    try:
            response = await client.chat.completions.create(
                model=CANDIDATE_MODEL,
                messages=[
                    {"role" : "system", "content" : system_instruction},
                    {"role" : "user", "content" : snippet_text},
                ],
                response_format={"type" : "json_object"},
                temperature=0.0
            )
            raw_json_string = response.choices[0].message.content
            
            try:
                extracted_data = json.loads(raw_json_string)
                parse_success = True
            
            except json.JSONDecodeError:
                extracted_data = None
                parse_success = False
            
            return {
                "raw_response" : raw_json_string,
                "parsed_response" : extracted_data,
                "parse_success" : parse_success,
                "usage": response.usage
            }
    
    except Exception as e:
            print(f"An API error occurred: {e}")
            return {}


async def prompt_few_shot(snippet_text: str) -> list[dict]:
    """Strategy 2 — few-shot. Include 2-3 worked examples in the prompt.
    Takes a natural language string and extracts transaction data using OpenAI.
    """

    system_instruction = """
    ROLE: You are an expert data extraction assistant specializing in HR recruitment.

    TASK:
    1. Analyze the user's natural language input.
    2. Extract three core fields:
        - "company" — the company doing the hiring.
        - "role" — the job title.
        - "years_experience_required" — the minimum experience required (integer).
    3. Gracefully correct common typos (e.g., "5+" -> "5").
    4. If the years of experience is not specified, set "years_experience_required" to null.

    CONTEXT: We get job snippets to identify the target roles.

    EXAMPLES:

    # Example 1: Spelling mistake + abbreviated experience
    User Input: "Infosys: Technical Project Manager. 
    Candidate shud have 8+ yrs exp managing software delivery projects. 
    PMP is a plus, along with good stakeholder mgmt skills."
    Output:
    {
        "company": "Infosys",
        "role": "Technical Project Manager",
        "years_experience_required": 8
    }

    Example 2: Common jargon + range
    User Input: "TCS is looking for a Business Analyst. 
    Need 4-6 yrs of relevant BA exp, preferably in BFSI. S
    hould be good at requirement gathering, BRDs and working with cross-functional teams."
    Output:
    {
        "company": "TCS",
        "role": "Business Analyst",
        "years_experience_required": 4
    }
    
    Example 3: Informal wording + "around"
    User Input: "Accenture - Cloud Architect. 
    We're looking for someone with around 10 years of exp in cloud infra. 
    AWS/Azure certs preferred. Strong hands-on and client facing skills reqd."
    Output:
    {
        "company": "Accenture",
        "role": "Cloud Architect",
        "years_experience_required": 10
    }

    FORMAT: Return ONLY a valid JSON object with the exact keys: "company", "role", "years_experience_required".
    
    """

    try:
        response = await client.chat.completions.create(
            model=CANDIDATE_MODEL,
            messages=[
                {"role" : "system", "content" : system_instruction},
                {"role" : "user", "content" : snippet_text},
            ],
            response_format={"type" : "json_object"},
            temperature=0.0
        )
        raw_json_string = response.choices[0].message.content
                    
        try:
            extracted_data = json.loads(raw_json_string)
            parse_success = True
                    
        except json.JSONDecodeError:
            extracted_data = None
            parse_success = False
                    
        return {
                "raw_response" : raw_json_string,
                "parsed_response" : extracted_data,
                "parse_success" : parse_success,
                "usage": response.usage
            }
            
    except Exception as e:
        print(f"An API error occurred: {e}")
        return {}


async def prompt_structured(snippet_text: str) -> list[dict]:
    """Strategy 3 — structured / role-based. Use a system prompt with a persona and explicit JSON schema.
       Takes a natural language string and extracts transaction data using OpenAI.
    """

    system_instruction = """
    ROLE: You are an expert data extraction assistant specializing in HR recruitment.

    TASK:
    1. Analyze the user's natural language input.
    2. Extract three core fields:
        - "company" — the company doing the hiring.
        - "role" — the job title.
        - "years_experience_required" — the minimum experience required (integer).
    3. Gracefully correct common typos (e.g., "5+" -> "5").
    4. If the years of experience is not specified, set "years_experience_required" to null.

    CONTEXT: We get job snippets to identify the target roles.

    EXAMPLES:
    OUTPUT: Return ONLY a valid JSON object with the exact keys: "company", "role", "years_experience_required".
    
    """

    try:
            response = await client.chat.completions.create(
                model=CANDIDATE_MODEL,
                messages=[
                    {"role" : "system", "content" : system_instruction},
                    {"role" : "user", "content" : snippet_text},
                ],
                response_format={"type" : "json_object"},
                temperature=0.0
            )
            raw_json_string = response.choices[0].message.content
                        
            try:
                extracted_data = json.loads(raw_json_string)
                parse_success = True
                        
            except json.JSONDecodeError:
                extracted_data = None
                parse_success = False
                        
            return {
                    "raw_response" : raw_json_string,
                    "parsed_response" : extracted_data,
                    "parse_success" : parse_success,
                    "usage": response.usage
                }
                
    except Exception as e:
        print(f"An API error occurred: {e}")
        return {}


async def prompt_cot(snippet_text: str) -> list[dict]:
    """Strategy 4 — Chain-of-Thought.
       Ask the model to reason step by step before extracting the data.
    """

    system_instruction = """
    You are an expert HR recruitment data extraction assistant.

    TASK:
    Analyze the job posting carefully and reason through the information step by
     step before producing the final answer.

    Follow this reasoning process:

    1. Identify the company that is hiring.
    2. Identify the exact job title or role being advertised.
    3. Identify all mentions of required years of experience.
    4. Determine the minimum required experience.
    - For a requirement such as "5+ years", use 5.
    - For a range such as "4-6 years", use 4.
    - For wording such as "around 10 years", use 10.
    - If multiple experience requirements are mentioned, use the overall minimum experience required for the role.
    5. Correct obvious spelling mistakes and normalize the extracted values.
    6. If the required years of experience is not specified, use null.

    Before returning the answer, verify that each extracted value is supported by the job posting.

    Return ONLY a valid JSON object with exactly these keys:
    {
        "company": "...",
        "role": "...",
        "years_experience_required": integer or null
    }

    Do not include explanations, reasoning, markdown, or any additional text in the response.
    """

    try:
            response = await client.chat.completions.create(
                model=CANDIDATE_MODEL,
                messages=[
                    {"role" : "system", "content" : system_instruction},
                    {"role" : "user", "content" : snippet_text},
                ],
                response_format={"type" : "json_object"},
                temperature=0.0
            )
            raw_json_string = response.choices[0].message.content
                        
            try:
                extracted_data = json.loads(raw_json_string)
                parse_success = True
                        
            except json.JSONDecodeError:
                extracted_data = None
                parse_success = False
                        
            return {
                    "raw_response" : raw_json_string,
                    "parsed_response" : extracted_data,
                    "parse_success" : parse_success,
                    "usage": response.usage
                }
                
    except Exception as e:
        print(f"An API error occurred: {e}")
        return {}


STRATEGIES = {
    'zero_shot': prompt_zero_shot,
    'few_shot': prompt_few_shot,
    'structured': prompt_structured,
    'cot': prompt_cot,
}

