# Supervised Fine-Tuning Data Formats for Qwen and Llama Models with DeepSpeed

Converting your custom JSONL data format to the required SFT formats for Qwen-2.5-7B-instruct and Llama-3.1-8B-instruct models is straightforward, as your existing structure already contains the essential components. The main differences lie in special token handling and minor format adjustments specific to each model.

Your current JSONL format with workflow_id, benchmark, data_indices, and messages array maps nearly directly to both models' requirements. The **messages array structure with role/content fields is exactly what both models expect**, requiring only minimal transformation to add model-specific metadata fields.

## Qwen-2.5-7B-Instruct Format Requirements

Qwen models use the ChatML (Chat Markup Language) format for fine-tuning. Each training sample must be formatted as a JSON object with a messages array, where each message contains role and content fields.

**Required JSONL Format:**
```json
{
  "type": "chatml",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me about large language models."},
    {"role": "assistant", "content": "Large language models are AI systems trained on vast amounts of text data..."}
  ],
  "source": "custom"
}
```

The **type field should be set to "chatml"** to indicate the format, while the source field identifies your data origin. When tokenized, Qwen uses specific special tokens: `<|im_start|>` marks the beginning of each message, `<|im_end|>` marks the end, and the tokenized format follows this pattern:

```
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Tell me about large language models.<|im_end|>
<|im_start|>assistant
Large language models are AI systems...<|im_end|>
```

For multi-turn conversations, simply extend the messages array with alternating user and assistant messages. **System prompts are optional but recommended** - they should always appear first if included. The model can function without system prompts but performs better with clear behavioral guidance.

## Llama-3.1-8B-Instruct Format Requirements

Llama models use a simpler JSON structure that requires only the messages array, making conversion from your format even more straightforward.

**Required JSONL Format:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "What is machine learning?"},
    {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence..."}
  ]
}
```

Llama 3.1 introduces support for four roles: system, user, assistant, and **ipython** (for tool/code execution). The tokenized format uses different special tokens: `<|begin_of_text|>` starts the sequence, `<|start_header_id|>` and `<|end_header_id|>` wrap role headers, and `<|eot_id|>` marks end of turn:

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

What is machine learning?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Machine learning is a subset of artificial intelligence...<|eot_id|>
```

**Double newlines after each header are critical** for proper formatting. System prompts follow the same optional-but-recommended pattern as Qwen.

## Python Code for Data Conversion

Here's a comprehensive conversion script that transforms your custom JSONL format to both model formats:

```python
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from transformers import AutoTokenizer

def convert_to_qwen_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert custom JSONL to Qwen 2.5 ChatML format."""
    return {
        "type": "chatml",
        "messages": data["messages"],
        "source": data.get("benchmark", "custom"),
        "workflow_id": data.get("workflow_id", "")
    }

def convert_to_llama_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert custom JSONL to Llama 3.1 format."""
    return {
        "messages": data["messages"]
    }

def validate_messages(messages: List[Dict[str, str]]) -> bool:
    """Validate message format for both models."""
    required_roles = {"system", "user", "assistant"}
    
    for msg in messages:
        if "role" not in msg or "content" not in msg:
            return False
        if msg["role"] not in required_roles:
            return False
    
    return True

def convert_jsonl_data(input_file: str, output_file: str, model_type: str):
    """Main conversion function."""
    converted_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                if not validate_messages(data["messages"]):
                    print(f"Warning: Line {line_num} has invalid message format")
                    continue
                
                if model_type.lower() == "qwen":
                    converted = convert_to_qwen_format(data)
                elif model_type.lower() == "llama":
                    converted = convert_to_llama_format(data)
                
                converted_data.append(converted)
                
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON on line {line_num}")
                continue
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Converted {len(converted_data)} samples to {output_file}")
```

For advanced tokenization with proper loss masking (only training on assistant responses):

```python
def prepare_training_data(messages, model_type, tokenizer, max_length=2048):
    """Tokenize with proper loss masking for training."""
    
    # Apply chat template
    text = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=False
    )
    
    # Tokenize full conversation
    tokenized = tokenizer(
        text, 
        truncation=True,
        max_length=max_length,
        padding="max_length",
        return_tensors="pt"
    )
    
    # Create labels with masking
    labels = tokenized["input_ids"].clone()
    
    if model_type == "qwen":
        # Find assistant response start for Qwen
        assistant_marker = "<|im_start|>assistant\n"
        assistant_start = text.find(assistant_marker)
        if assistant_start != -1:
            prefix_tokens = tokenizer.encode(text[:assistant_start], add_special_tokens=False)
            labels[:len(prefix_tokens)] = -100
            
    elif model_type == "llama":
        # Find assistant response start for Llama
        assistant_marker = "<|start_header_id|>assistant<|end_header_id|>"
        assistant_start = text.find(assistant_marker)
        if assistant_start != -1:
            prefix_text = text[:assistant_start + len(assistant_marker)]
            prefix_tokens = tokenizer.encode(prefix_text, add_special_tokens=False)
            labels[:len(prefix_tokens)] = -100
    
    return {
        "input_ids": tokenized["input_ids"],
        "attention_mask": tokenized["attention_mask"], 
        "labels": labels
    }
```

## DeepSpeed Training Configuration

Both models benefit from DeepSpeed's ZeRO optimization for memory-efficient training. Here's the recommended configuration for ZeRO Stage 3:

```json
{
    "zero_optimization": {
        "stage": 3,
        "overlap_comm": true,
        "contiguous_gradients": true,
        "reduce_bucket_size": 5e8,
        "stage3_prefetch_bucket_size": 5e8,
        "stage3_param_persistence_threshold": 1e6
    },
    "bf16": {
        "enabled": true
    },
    "train_micro_batch_size_per_gpu": 1,
    "gradient_accumulation_steps": 8,
    "gradient_clipping": 1.0,
    "optimizer": {
        "type": "AdamW",
        "params": {
            "lr": 2e-4,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "weight_decay": 0.1
        }
    }
}
```

For training with this configuration:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from torch.utils.data import Dataset

class SFTDataset(Dataset):
    def __init__(self, data_path, tokenizer, model_type, max_length=2048):
        self.tokenizer = tokenizer
        self.model_type = model_type
        self.max_length = max_length
        self.data = []
        
        with open(data_path, 'r') as f:
            for line in f:
                self.data.append(json.loads(line.strip()))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return prepare_training_data(
            self.data[idx]["messages"], 
            self.model_type, 
            self.tokenizer, 
            self.max_length
        )

# Training setup
model_name = "Qwen/Qwen2.5-7B-Instruct"  # or "meta-llama/Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16)

training_args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
    bf16=True,
    deepspeed="deepspeed_config.json"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=SFTDataset("converted_data.jsonl", tokenizer, "qwen"),
    tokenizer=tokenizer
)

trainer.train()
```

## Best practices for handling system prompts

System prompts establish the model's behavior and capabilities. While optional for both models, they significantly improve response quality and consistency.

**Effective system prompt patterns:**

For general assistance:
```json
{"role": "system", "content": "You are a helpful assistant."}
```

For specialized domains:
```json
{"role": "system", "content": "You are an expert programmer. Provide clear, efficient code solutions with explanations."}
```

For tool use (Llama 3.1):
```json
{"role": "system", "content": "Environment: ipython\nTools: brave_search, wolfram_alpha\nYou are a helpful assistant with access to web search and computation tools."}
```

**Key guidelines:** Keep system prompts consistent across your dataset, be specific about desired behaviors, and place them first in the conversation. For Qwen, the default system prompt references being created by Alibaba Cloud, while Llama models have no default system message.

## Critical implementation details

Several common pitfalls can derail fine-tuning efforts. **Always apply the proper chat template** rather than manually formatting messages - this ensures correct special token placement. When creating training labels, **mask all tokens except assistant responses** to prevent the model from learning to generate prompts.

For memory optimization with large models, use gradient checkpointing and DeepSpeed ZeRO-3. **QLoRA works better with ZeRO-2** due to quantization interactions. Monitor sequence lengths carefully - Qwen defaults to 8192 tokens while Llama supports up to 128K, but longer sequences require more memory.

The most critical formatting difference is in special tokens: Qwen uses `<|im_end|>` as its end-of-sequence token, while Llama uses `<|eot_id|>`. Using the wrong tokens will cause generation to fail or produce garbled output.

With these specifications and code examples, you can successfully convert your custom JSONL data for supervised fine-tuning of both Qwen-2.5-7B-instruct and Llama-3.1-8B-instruct models using DeepSpeed. The conversion process is straightforward - your existing format already contains the core components both models require.