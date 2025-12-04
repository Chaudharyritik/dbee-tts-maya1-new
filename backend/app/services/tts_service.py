import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from snac import SNAC
import io
import scipy.io.wavfile
import numpy as np
import os
import traceback

# Maya1 Constants
CODE_START_TOKEN_ID = 128257
CODE_END_TOKEN_ID = 128258
CODE_TOKEN_OFFSET = 128266
SNAC_MIN_ID = 128266
SNAC_MAX_ID = 156937
SNAC_TOKENS_PER_FRAME = 7
SOH_ID = 128259
EOH_ID = 128260
SOA_ID = 128261
BOS_ID = 128000
TEXT_EOT_ID = 128009

class TTSService:
    def __init__(self):
        self.model_id = os.getenv("MODEL_PATH", "maya-research/maya1")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Maya1 model from {self.model_id} on {self.device}...")
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
            
            print("Loading SNAC decoder...")
            self.snac_model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval().to(self.device)
            
            print("Maya1 model and SNAC decoder loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

    def build_prompt(self, description: str, text: str) -> str:
        """Build formatted prompt for Maya1."""
        soh_token = self.tokenizer.decode([SOH_ID])
        eoh_token = self.tokenizer.decode([EOH_ID])
        soa_token = self.tokenizer.decode([SOA_ID])
        sos_token = self.tokenizer.decode([CODE_START_TOKEN_ID])
        eot_token = self.tokenizer.decode([TEXT_EOT_ID])
        bos_token = self.tokenizer.bos_token
        
        formatted_text = f'<description="{description}"> {text}'
        prompt = (
            soh_token + bos_token + formatted_text + eot_token + eoh_token + soa_token + sos_token
        )
        return prompt

    def extract_snac_codes(self, token_ids: list) -> list:
        """Extract SNAC codes from generated tokens."""
        try:
            eos_idx = token_ids.index(CODE_END_TOKEN_ID)
        except ValueError:
            eos_idx = len(token_ids)
            
        snac_codes = [
            token_id for token_id in token_ids[:eos_idx]
            if SNAC_MIN_ID <= token_id <= SNAC_MAX_ID
        ]
        return snac_codes

    def unpack_snac_from_7(self, snac_tokens: list) -> list:
        """Unpack 7-token SNAC frames to 3 hierarchical levels."""
        if snac_tokens and snac_tokens[-1] == CODE_END_TOKEN_ID:
            snac_tokens = snac_tokens[:-1]
            
        frames = len(snac_tokens) // SNAC_TOKENS_PER_FRAME
        snac_tokens = snac_tokens[:frames * SNAC_TOKENS_PER_FRAME]
        
        if frames == 0:
            return [[], [], []]
            
        l1, l2, l3 = [], [], []
        for i in range(frames):
            slots = snac_tokens[i*7:(i+1)*7]
            # Apply offset and modulo 4096 as per official code
            l1.append((slots[0] - CODE_TOKEN_OFFSET) % 4096)
            l2.extend([
                (slots[1] - CODE_TOKEN_OFFSET) % 4096,
                (slots[4] - CODE_TOKEN_OFFSET) % 4096,
            ])
            l3.extend([
                (slots[2] - CODE_TOKEN_OFFSET) % 4096,
                (slots[3] - CODE_TOKEN_OFFSET) % 4096,
                (slots[5] - CODE_TOKEN_OFFSET) % 4096,
                (slots[6] - CODE_TOKEN_OFFSET) % 4096,
            ])
            
        return [l1, l2, l3]

    def synthesize(self, text: str, voice_description: str, speed: float = 1.0) -> bytes:
        try:
            # Use default description if empty
            if not voice_description:
                voice_description = "Generic female voice"
            
            # Clean text
            text = text.strip()
            text = " ".join(text.split()) # Normalize whitespace
            text = text.replace(" ,", ",") # Fix spacing before commas
            text = text.replace(" .", ".") # Fix spacing before periods
                
            print(f"Synthesizing: '{text}' with voice: '{voice_description}'")
            
            prompt = self.build_prompt(voice_description, text)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=2048,
                    min_new_tokens=28, # At least 4 frames
                    temperature=0.3, # Increased from 0.2 to restore expressiveness
                    top_p=0.95, # Increased from 0.9 to allow more diverse tokens
                    repetition_penalty=1.1, # Reduced from 1.2 to avoid penalizing style tokens
                    do_sample=True,
                    eos_token_id=CODE_END_TOKEN_ID,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
                
                # Strip input tokens
                generated_ids = output[0, inputs.input_ids.shape[1]:].tolist()
                print(f"Generated {len(generated_ids)} tokens")
                
                # Extract and unpack SNAC codes
                snac_tokens = self.extract_snac_codes(generated_ids)
                print(f"Extracted {len(snac_tokens)} SNAC tokens")
                
                if len(snac_tokens) < 7:
                    raise ValueError("Not enough SNAC tokens generated")
                    
                levels = self.unpack_snac_from_7(snac_tokens)
                
                # Convert to tensors
                codes_tensor = [
                    torch.tensor(level, dtype=torch.long, device=self.device).unsqueeze(0)
                    for level in levels
                ]
                
                # Decode to audio
                z_q = self.snac_model.quantizer.from_codes(codes_tensor)
                audio = self.snac_model.decoder(z_q)[0, 0].cpu().numpy()
                
                # Trim warmup samples (first 2048 samples)
                if len(audio) > 2048:
                    audio = audio[2048:]
            
            sample_rate = 24000
            
            # Normalize
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            
            # Convert to int16
            audio_int16 = (audio * 32767).astype(np.int16)
            
            byte_io = io.BytesIO()
            scipy.io.wavfile.write(byte_io, sample_rate, audio_int16)
            return byte_io.getvalue()
            
        except Exception as e:
            print(f"ERROR in synthesize: {e}")
            traceback.print_exc()
            raise e
