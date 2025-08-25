1. /nas/models/Meta-Llama-3.1-8B-Instruct
```
{
  "bos_token_id": 128000,
  "do_sample": true,
  "eos_token_id": [
    128001,
    128008,
    128009
  ],
  "temperature": 0.6,
  "top_p": 0.9,
  "transformers_version": "4.42.3"
}
```
and
```
(base) root@ctyun172022236189:/nas/models/Meta-Llama-3.1-8B-Instruct# ls
config.json             LICENSE                           model-00003-of-00004.safetensors  original                 tokenizer_config.json
configuration.json      model-00001-of-00004.safetensors  model-00004-of-00004.safetensors  README.md                tokenizer.json
generation_config.json  model-00002-of-00004.safetensors  model.safetensors.index.json      special_tokens_map.json  USE_POLICY.md
```

2. /nas/models/Qwen2.5-7B-Instruct
```
{
  "bos_token_id": 151643,
  "pad_token_id": 151643,
  "do_sample": true,
  "eos_token_id": [
    151645,
    151643
  ],
  "repetition_penalty": 1.05,
  "temperature": 0.7,
  "top_p": 0.8,
  "top_k": 20,
  "transformers_version": "4.37.0"
}
```
and
```
(base) root@ctyun172022236189:/nas/models/Qwen2.5-7B-Instruct# ls
config.json             LICENSE                           model-00002-of-00004.safetensors  model.safetensors.index.json  tokenizer.json
configuration.json      merges.txt                        model-00003-of-00004.safetensors  README.md                     vocab.json
generation_config.json  model-00001-of-00004.safetensors  model-00004-of-00004.safetensors  tokenizer_config.json
```

3. /nas/models/Qwen3-8B
```
{
    "bos_token_id": 151643,
    "do_sample": true,
    "eos_token_id": [
        151645,
        151643
    ],
    "pad_token_id": 151643,
    "temperature": 0.6,
    "top_k": 20,
    "top_p": 0.95,
    "transformers_version": "4.51.0"
}
```
and
```
(base) root@ctyun172022236189:/nas/models/Qwen3-8B# ls
config.json             merges.txt                        model-00004-of-00005.safetensors  README.md
configuration.json      model-00001-of-00005.safetensors  model-00005-of-00005.safetensors  tokenizer_config.json
generation_config.json  model-00002-of-00005.safetensors  model.safetensors.index.json      tokenizer.json
LICENSE                 model-00003-of-00005.safetensors  outputs                           vocab.json
```
