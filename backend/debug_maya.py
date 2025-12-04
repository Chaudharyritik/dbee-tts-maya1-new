import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import time

# Constants
CODE_START_TOKEN_ID = 128257
CODE_END_TOKEN_ID = 128258
SOH_ID = 128259
EOH_ID = 128260
SOA_ID = 128261
BOS_ID = 128000
TEXT_EOT_ID = 128009

def build_prompt(tokenizer, description: str, text: str) -> str:
    soh_token = tokenizer.decode([SOH_ID])
    eoh_token = tokenizer.decode([EOH_ID])
    soa_token = tokenizer.decode([SOA_ID])
    sos_token = tokenizer.decode([CODE_START_TOKEN_ID])
    eot_token = tokenizer.decode([TEXT_EOT_ID])
    bos_token = tokenizer.bos_token
    
    formatted_text = f'<description="{description}"> {text}'
    prompt = (
        soh_token + bos_token + formatted_text + eot_token + eoh_token + soa_token + sos_token
    )
    return prompt

def main():
    model_id = os.getenv("MODEL_PATH", "maya-research/maya1")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model from {model_id} on {device}...")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to(device)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    text = "are you liesting <whisper> , how are you <gasp> , happy birthday <laugh>"
    voice_description = "Young British female, energetic"
    
    print(f"\nInput Text: '{text}'")
    print(f"Voice: '{voice_description}'")

    prompt = build_prompt(tokenizer, voice_description, text)
    print(f"Prompt: {prompt}")
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    print("\nGenerating...")
    start_time = time.time()
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=2048,
            min_new_tokens=28,
            temperature=0.2, # Updated to match service
            top_p=0.9,
            repetition_penalty=1.2, # Updated to match service
            do_sample=True,
            eos_token_id=CODE_END_TOKEN_ID,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    end_time = time.time()
    generated_ids = output[0, inputs.input_ids.shape[1]:].tolist()
    
    print(f"\nGeneration took {end_time - start_time:.2f} seconds")
    print(f"Generated {len(generated_ids)} tokens")
    
    if len(generated_ids) >= 2048:
        print("WARNING: Hit max_new_tokens limit! Model likely hallucinating/looping.")
    elif generated_ids[-1] == CODE_END_TOKEN_ID:
        print("Success: Model stopped with CODE_END_TOKEN_ID.")
    else:
        print(f"Stopped for unknown reason. Last token: {generated_ids[-1]}")

if __name__ == "__main__":
    main()
