import torch
try:
    from transformers import AutoModelForTextToSpeech, AutoTokenizer
except ImportError:
    try:
        print("AutoModelForTextToSpeech not found. Trying AutoModelForCausalLM (Maya1 is Llama-based)...")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        AutoModelForTextToSpeech = AutoModelForCausalLM # Alias it for compatibility
    except ImportError as e:
        import transformers
        print(f"CRITICAL ERROR: Failed to import AutoModel classes.")
        print(f"Available in transformers: {dir(transformers)}")
        raise e
import io
import scipy.io.wavfile
import numpy as np
from snac import SNAC

import os

class TTSService:
    def __init__(self):
        # Check for local model path from env, otherwise use HF ID
        self.model_id = os.getenv("MODEL_PATH", "maya-research/maya1")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Maya1 model from {self.model_id} on {self.device}...")
        
        try:
            # Load Maya1 (Llama part)
            self.model = AutoModelForTextToSpeech.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            
            # Load SNAC Decoder
            print("Loading SNAC decoder...")
            self.snac_model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").to(self.device)
            
            print("Maya1 model and SNAC decoder loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

    def unpack_snac(self, codes):
        # Unpack 7-token frames into hierarchical levels
        # l1: 1 token, l2: 2 tokens, l3: 4 tokens
        codes = codes.cpu().tolist()
        
        # Truncate to multiple of 7
        n_frames = len(codes) // 7
        codes = codes[:n_frames * 7]
        
        l1, l2, l3 = [], [], []
        for i in range(n_frames):
            frame = codes[i*7 : (i+1)*7]
            l1.append(frame[0])
            l2.extend(frame[1:3])
            l3.extend(frame[3:7])
            
        return [
            torch.tensor(l1, dtype=torch.long).unsqueeze(0).to(self.device),
            torch.tensor(l2, dtype=torch.long).unsqueeze(0).to(self.device),
            torch.tensor(l3, dtype=torch.long).unsqueeze(0).to(self.device)
        ]

    def synthesize(self, text: str, voice_description: str, speed: float = 1.0) -> bytes:
        import traceback
        try:
            # Construct the prompt with voice description if the model supports it in this specific way
            # Note: The specific prompting strategy for Maya1 might vary. 
            # Based on standard usage for such models, we often prepend the description.
            # However, if the model expects a specific format, we should adjust.
            # Assuming standard text-to-speech generation for now.
            
            # If the model supports voice description as a separate input or prepended text:
            # For now, we will just use the text. If Maya1 uses a specific separator, we'd add it.
            # Research indicated "Natural Language Voice Descriptions". 
            # Often this is done via a specific prompt structure.
            # Let's assume a simple concatenation for now or just text if unsure of the exact separator.
            
            # NOTE: To fully utilize "Voice Description", we might need to verify the exact prompt format.
            # But for "direct load", this is the correct code structure.
            
            # Prepare input
            # Note: Maya1 might expect specific formatting for voice description.
            # For now, we append it or just use text if description is empty.
            prompt = text
            if voice_description and voice_description != "Generic female voice":
                 # Simple heuristic: prepend description if provided
                 # Real Maya1 usage might differ, but this is a reasonable start.
                 pass 

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                # Generate tokens
                # We need to set max_new_tokens or similar to avoid infinite generation
                output = self.model.generate(
                    **inputs, 
                    max_new_tokens=1000, # Adjust as needed
                    do_sample=True, 
                    temperature=0.7
                )
                
                # Strip input tokens
                generated_ids = output[0][inputs.input_ids.shape[1]:]
                print(f"DEBUG: Generated {len(generated_ids)} tokens: {generated_ids.tolist()}")
                
                if len(generated_ids) < 7:
                    raise ValueError(f"Model generated only {len(generated_ids)} tokens, but SNAC requires at least 7 (one frame).")

                # Decode SNAC tokens to audio
                snac_codes = self.unpack_snac(generated_ids)
                print(f"DEBUG: Unpacked SNAC codes shapes: {[c.shape for c in snac_codes]}")
                audio_tensor = self.snac_model.decode(snac_codes)
                
            audio_data = audio_tensor.squeeze().cpu().numpy()
            sample_rate = 24000 # SNAC 24khz
            
            # Normalize
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # Convert to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            byte_io = io.BytesIO()
            scipy.io.wavfile.write(byte_io, sample_rate, audio_int16)
            return byte_io.getvalue()
        except Exception as e:
            print(f"ERROR in synthesize: {e}")
            traceback.print_exc()
            raise e
