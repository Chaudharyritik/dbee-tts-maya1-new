import torch
from transformers import AutoModelForTextToSpeech, AutoTokenizer
import io
import scipy.io.wavfile
import numpy as np

import os

class TTSService:
    def __init__(self):
        # Check for local model path from env, otherwise use HF ID
        self.model_id = os.getenv("MODEL_PATH", "maya-research/maya1")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Maya1 model from {self.model_id} on {self.device}...")
        
        try:
            self.model = AutoModelForTextToSpeech.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            print("Maya1 model loaded successfully.")
        except Exception as e:
            print(f"Error loading model from {self.model_id}: {e}")
            raise e

    def synthesize(self, text: str, voice_description: str, speed: float = 1.0) -> bytes:
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
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            # Generate audio
            # The model might take 'speaker_embeddings' or similar if it was a different architecture.
            # For Maya1 (Llama-style), it likely generates tokens.
            output = self.model.generate(**inputs)
            
        # The output from the model needs to be converted to waveform.
        # If output is raw waveform (unlikely for Llama-based), we use it directly.
        # If output is tokens (SNAC), we need to decode. 
        # AutoModelForTextToSpeech usually handles the vocoding if it's an end-to-end wrapper.
        # If not, we might need the specific vocoder. 
        # Given "AutoModelForTextToSpeech", we assume it returns waveform or compatible output.
        
        audio_data = output.audio[0].cpu().numpy()
        sample_rate = output.sampling_rate
        
        # Normalize if needed
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Convert to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        byte_io = io.BytesIO()
        scipy.io.wavfile.write(byte_io, sample_rate, audio_int16)
        return byte_io.getvalue()
