from transformers import AutoTokenizer
import os

def main():
    model_id = os.getenv("MODEL_PATH", "maya-research/maya1")
    print(f"Loading tokenizer from {model_id}...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    except Exception as e:
        print(f"Failed to load tokenizer: {e}")
        return

    # Structural tokens
    SOH_ID = 128259
    EOH_ID = 128260
    SOA_ID = 128261
    CODE_START_TOKEN_ID = 128257
    TEXT_EOT_ID = 128009
    tags = ["<laugh>", "<whisper>", "<gasp>", "<cry>", "<sigh>", "<angry>"]
    
    special_ids = {
        "SOH": SOH_ID,
        "EOH": EOH_ID,
        "SOA": SOA_ID,
        "SOS": CODE_START_TOKEN_ID,
        "EOT": TEXT_EOT_ID
    }
    
    print("\nChecking structural tokens round-trip:")
    for name, tid in special_ids.items():
        decoded = tokenizer.decode([tid])
        re_encoded = tokenizer.encode(decoded, add_special_tokens=False)
        print(f"{name} ({tid}) -> '{decoded}' -> {re_encoded}")
        
        if len(re_encoded) != 1 or re_encoded[0] != tid:
            print(f"  ERROR: {name} round-trip failed! Got {re_encoded} instead of [{tid}]")
        else:
            print(f"  OK: {name} round-trip successful.")

    print("\nChecking tags:")
    for tag in tags:
        ids = tokenizer.encode(tag, add_special_tokens=False)
        tokens = tokenizer.convert_ids_to_tokens(ids)
        print(f"Tag: '{tag}' -> IDs: {ids} -> Tokens: {tokens}")
        
        if len(ids) > 1:
            print(f"  WARNING: '{tag}' is split into multiple tokens!")
        else:
            print(f"  OK: '{tag}' is a single token.")

if __name__ == "__main__":
    main()
