"""Download and process OlympiadBench dataset"""
import json
import os
from datasets import load_dataset

def download_and_process_olympiadbench():
    """Download OlympiadBench dataset and save in JSONL format"""
    print("正在下载 math-ai/OlympiadBench 数据集...")

    try:
        # Load the dataset from Hugging Face
        dataset = load_dataset("math-ai/OlympiadBench", split="test")
        print(f"成功下载数据集，共 {len(dataset)} 个问题")

        # Create output directory
        output_dir = "Processed_dataset/high_level_math/olympiadbench"
        os.makedirs(output_dir, exist_ok=True)

        # Process and save data
        processed_data = []
        for idx, item in enumerate(dataset):
            # Extract question and answer
            processed_item = {
                "question": item.get("problem", ""),
                "answer": item.get("answer", ""),
                "index": idx
            }

            # Add additional metadata if available
            if "solution" in item:
                processed_item["solution"] = item["solution"]
            if "subject" in item:
                processed_item["subject"] = item["subject"]
            if "difficulty" in item:
                processed_item["difficulty"] = item["difficulty"]

            processed_data.append(processed_item)

        # Save as JSONL in both locations
        # 1. In the main high_level_math directory
        output_file1 = "Processed_dataset/high_level_math/olympiadbench.jsonl"
        with open(output_file1, 'w', encoding='utf-8') as f:
            for item in processed_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"已保存到 {output_file1}")

        # 2. In the olympiadbench subdirectory
        output_file2 = os.path.join(output_dir, "olympiadbench.jsonl")
        with open(output_file2, 'w', encoding='utf-8') as f:
            for item in processed_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"已保存到 {output_file2}")

        return processed_data

    except Exception as e:
        print(f"下载或处理数据集时出错: {e}")
        return None

if __name__ == "__main__":
    data = download_and_process_olympiadbench()
    if data:
        print(f"处理完成，共 {len(data)} 个问题")
        # Show first few examples
        print("\n前3个示例:")
        for i in range(min(3, len(data))):
            print(f"\n问题 {i+1}:")
            print(f"Question: {data[i]['question'][:200]}...")
            if data[i]['answer']:
                print(f"Answer: {data[i]['answer'][:100]}...")