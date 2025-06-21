### HotpotQA env setup
```text
cd HotpotQA
# Create directory for data
mkdir -p data/corpus/kilt

# Download corpus and index (using Hugging Face CLI or web download)
huggingface-cli download corag/kilt-corpus
huggingface-cli download russwest404/kilt_index --local-dir data/corpus/kilt
# Edit script to modify INDEX_PATH
export INDEX_PATH="../../data/corpus/kilt/kilt_index_IVF16384_PQ64.bin"

cd kilt_search_server
bash run_search_api.sh
```

代码来自https://github.com/0russwest0/Agent-R1