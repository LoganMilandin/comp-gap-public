import argparse
import json
import openai
import os
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from tqdm import tqdm

openai.api_key = os.environ["OPENAI_API_KEY"]

def load_jsonl(path):
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data

def write_list_to_jsonl(outputs, path="output.jsonl"):
    with open(path, "w") as f:
        for d in outputs:
            f.write(json.dumps(d) + "\n")
    
def format_prompt(demo):
    prompt = ""
    for d in demo:
        prompt += f"{d['Question']} {d['Answer']}\n"
    print("prompt: ", prompt)
    return prompt

def api_inference(input):
    system_prompt = f"You are ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture.\nKnowledge cutoff: 2021-09\nCurrent date: 2023-04-21"
    current_model = "gpt-3.5-turbo"

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(**kwargs):
        return openai.ChatCompletion.create(**kwargs)
    
    ans = completion_with_backoff(
        model=current_model,
        max_tokens=3,
        stop='\n',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input}
        ]
    )
    response_text = ans['choices'][0]["message"]["content"]
    output = response_text.strip() #.split("\n")[0].strip()
    return output

def inference(data, fewshot=False):
    random.shuffle(data)

    if fewshot:
        demo = data[:fewshot]
        prompt = format_prompt(demo)
        test_data = data[fewshot:]
    else:
        test_data = data
        prompt = ''

    evaluated = []
    for expression in tqdm(test_data):
        input = "{} ".format(expression["Question"])
        instruction = "Solve the arithmetic expression following the examples. Don't show your work. Numerical answers only! GIve your answer in the format \"The final answer is <answer>\".\n"
        new_input = f"{instruction}{prompt}{input}"
        print(new_input)
        output = api_inference(new_input)
        expression["pred"] = output
        evaluated.append(expression)

    return evaluated


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_path', help='path to the evaluation benchmark')
    parser.add_argument('--output_dir', help='path to output dir for eval results')
    args = parser.parse_args()

    dataset_path = args.dataset_path
    output_dir = args.output_dir
    data = load_jsonl(dataset_path)

    evaluations = inference(data)
    output_path = os.path.join(output_dir, f"evaluated_{dataset_path.split('/')[-1]}")

    write_list_to_jsonl(evaluations, output_path)



