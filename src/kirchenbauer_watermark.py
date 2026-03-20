"""Real Kirchenbauer et al. (2023) green-list watermarking with logit access.

Implements the actual algorithm:
1. For each token position, hash the previous token to create a seed
2. Use the seed to partition vocabulary into green/red lists (gamma fraction green)
3. Add delta to green-list token logits before sampling
4. Detection: count green-list tokens and compute z-score

This requires logit access (HuggingFace model), unlike the v1 synonym simulation.
"""
import hashlib
from typing import Optional

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def _get_green_list(prev_token_id: int, vocab_size: int, gamma: float = 0.5,
                    hash_key: int = 42) -> set:
    """Deterministic green-list partition based on previous token."""
    seed_str = f"{hash_key}-{prev_token_id}"
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    green_size = int(gamma * vocab_size)
    green_indices = set(rng.choice(vocab_size, size=green_size, replace=False).tolist())
    return green_indices


class KirchenbauerWatermark:
    """Watermarked text generation using Kirchenbauer green-list method."""

    def __init__(self, model_name: str = "gpt2", gamma: float = 0.5,
                 delta: float = 2.0, hash_key: int = 42, device: str = "cpu"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.model.eval()
        self.gamma = gamma
        self.delta = delta
        self.hash_key = hash_key
        self.device = device
        self.vocab_size = self.tokenizer.vocab_size

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_watermarked(self, prompt: str, max_new_tokens: int = 200,
                             temperature: float = 1.0) -> str:
        """Generate text with watermark (biased toward green-list tokens)."""
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        generated = input_ids[0].tolist()

        with torch.no_grad():
            for _ in range(max_new_tokens):
                inputs = torch.tensor([generated], device=self.device)
                outputs = self.model(inputs)
                logits = outputs.logits[0, -1, :]  # logits for next token

                # Get green list based on previous token
                prev_token = generated[-1]
                green_list = _get_green_list(prev_token, self.vocab_size,
                                             self.gamma, self.hash_key)

                # Add delta to green-list logits (the watermark)
                for idx in green_list:
                    logits[idx] += self.delta

                # Sample from modified distribution
                if temperature > 0:
                    probs = torch.softmax(logits / temperature, dim=-1)
                    next_token = torch.multinomial(probs, 1).item()
                else:
                    next_token = logits.argmax().item()

                generated.append(next_token)

                # Stop at EOS
                if next_token == self.tokenizer.eos_token_id:
                    break

        # Decode only the generated tokens (not the prompt)
        return self.tokenizer.decode(generated[input_ids.shape[1]:],
                                     skip_special_tokens=True)

    def generate_unwatermarked(self, prompt: str, max_new_tokens: int = 200,
                               temperature: float = 1.0) -> str:
        """Generate text WITHOUT watermark (normal sampling)."""
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        generated = input_ids[0].tolist()

        with torch.no_grad():
            for _ in range(max_new_tokens):
                inputs = torch.tensor([generated], device=self.device)
                outputs = self.model(inputs)
                logits = outputs.logits[0, -1, :]

                if temperature > 0:
                    probs = torch.softmax(logits / temperature, dim=-1)
                    next_token = torch.multinomial(probs, 1).item()
                else:
                    next_token = logits.argmax().item()

                generated.append(next_token)
                if next_token == self.tokenizer.eos_token_id:
                    break

        return self.tokenizer.decode(generated[input_ids.shape[1]:],
                                     skip_special_tokens=True)

    def detect(self, text: str, threshold: float = 4.0,
               prompt_tokens: Optional[int] = None) -> dict:
        """Detect watermark by counting green-list token fraction.

        Uses z-score test: z = (|green| - gamma * T) / sqrt(T * gamma * (1-gamma))
        where T = number of tokens scored.
        """
        token_ids = self.tokenizer.encode(text)

        # Skip first token (no previous token to hash against)
        start = max(1, prompt_tokens or 1)
        if len(token_ids) <= start:
            return {"z_score": 0.0, "green_fraction": 0.0, "num_tokens_scored": 0,
                    "green_count": 0, "detected": False}

        green_count = 0
        num_scored = 0

        for i in range(start, len(token_ids)):
            prev_token = token_ids[i - 1]
            green_list = _get_green_list(prev_token, self.vocab_size,
                                         self.gamma, self.hash_key)
            if token_ids[i] in green_list:
                green_count += 1
            num_scored += 1

        if num_scored == 0:
            return {"z_score": 0.0, "green_fraction": 0.0, "num_tokens_scored": 0,
                    "green_count": 0, "detected": False}

        green_fraction = green_count / num_scored
        # z-score under null (no watermark): expected green fraction = gamma
        expected = self.gamma * num_scored
        std = np.sqrt(num_scored * self.gamma * (1 - self.gamma))
        z_score = (green_count - expected) / std if std > 0 else 0.0

        return {
            "z_score": float(z_score),
            "green_fraction": float(green_fraction),
            "green_count": int(green_count),
            "num_tokens_scored": int(num_scored),
            "detected": z_score > threshold,
        }
