#!/usr/bin/env python3
"""
Exact token counting using actual Qwen and Llama tokenizers.
This gives you the REAL token counts, not estimates.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
from transformers import AutoTokenizer
from tqdm import tqdm
import argparse
import sys

def count_exact_tokens(messages: List[Dict[str, str]], tokenizer) -> Dict[str, Any]:
    """
    Count exact tokens using the actual tokenizer with chat template.
    This mirrors what happens during training.
    """
    stats = {}
    
    # 1. Count raw characters for reference
    total_chars = sum(len(msg.get('content', '')) for msg in messages)
    stats['total_chars'] = total_chars
    
    # 2. Apply chat template (this is what actually gets tokenized during training)
    try:
        # This is the EXACT format that will be used in training
        formatted_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        stats['formatted_text'] = formatted_text
        stats['formatted_chars'] = len(formatted_text)
        
        # 3. Tokenize the formatted text (this is the REAL token count)
        tokens = tokenizer.encode(
            formatted_text,
            add_special_tokens=True,  # Include special tokens
            truncation=False,  # Don't truncate - we want to see the full length
            return_tensors=None
        )
        stats['exact_token_count'] = len(tokens)
        stats['tokens'] = tokens  # Store actual token IDs if needed
        
        # 4. Calculate the actual chars-to-tokens ratio
        stats['chars_per_token'] = total_chars / len(tokens) if len(tokens) > 0 else 0
        
        # 5. Decode back to verify
        decoded_text = tokenizer.decode(tokens, skip_special_tokens=False)
        stats['decoded_length'] = len(decoded_text)
        
    except Exception as e:
        print(f"Error applying chat template: {e}")
        # Fallback: tokenize each message separately
        total_tokens = 0
        for msg in messages:
            content = msg.get('content', '')
            tokens = tokenizer.encode(content, add_special_tokens=False)
            total_tokens += len(tokens)
        stats['exact_token_count'] = total_tokens
        stats['chars_per_token'] = total_chars / total_tokens if total_tokens > 0 else 0
        stats['note'] = "Fallback method - no chat template"
    
    return stats

def analyze_dataset_with_tokenizer(
    jsonl_path: str,
    model_path: str,
    model_type: str = "auto",
    sample_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyze entire dataset with actual tokenizer.
    
    Args:
        jsonl_path: Path to JSONL file
        model_path: Path to model/tokenizer (local or HuggingFace)
        model_type: "qwen" or "llama" or "auto"
        sample_size: If set, only analyze first N samples
    """
    print("="*80)
    print(f"📊 Exact Token Analysis")
    print("="*80)
    print(f"Dataset: {jsonl_path}")
    print(f"Model: {model_path}")
    print(f"Type: {model_type}")
    
    # Load tokenizer
    print("\n🔄 Loading tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            use_fast=True
        )
        print(f"✅ Tokenizer loaded: {tokenizer.__class__.__name__}")
        print(f"   Vocab size: {len(tokenizer):,} tokens")
        
        # Set pad token if needed
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print("   Set pad_token = eos_token")
            
    except Exception as e:
        print(f"❌ Error loading tokenizer: {e}")
        return {}
    
    # Process dataset
    print(f"\n📂 Processing dataset...")
    results = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    total_samples = len(lines)
    if sample_size:
        lines = lines[:sample_size]
        print(f"   Analyzing first {sample_size} of {total_samples} samples")
    else:
        print(f"   Analyzing all {total_samples} samples")
    
    for idx, line in enumerate(tqdm(lines, desc="Processing samples")):
        if not line.strip():
            continue
            
        try:
            data = json.loads(line)
            messages = data.get('messages', [])
            
            # Get exact token count
            token_stats = count_exact_tokens(messages, tokenizer)
            
            # Store results
            result = {
                'sample_idx': idx,
                'exact_tokens': token_stats['exact_token_count'],
                'total_chars': token_stats['total_chars'],
                'formatted_chars': token_stats.get('formatted_chars', 0),
                'chars_per_token': token_stats['chars_per_token'],
                'num_messages': len(messages),
            }
            
            # Add metadata if available
            if 'workflow_id' in data:
                result['workflow_id'] = data['workflow_id']
            if 'benchmark' in data:
                result['benchmark'] = data['benchmark']
                
            results.append(result)
            
        except Exception as e:
            print(f"\n⚠️ Error processing line {idx}: {e}")
            continue
    
    # Calculate statistics
    if results:
        token_counts = [r['exact_tokens'] for r in results]
        char_counts = [r['total_chars'] for r in results]
        ratios = [r['chars_per_token'] for r in results]
        
        stats = {
            'num_samples': len(results),
            'token_stats': {
                'min': min(token_counts),
                'max': max(token_counts),
                'mean': np.mean(token_counts),
                'median': np.median(token_counts),
                'std': np.std(token_counts),
                'p25': np.percentile(token_counts, 25),
                'p75': np.percentile(token_counts, 75),
                'p90': np.percentile(token_counts, 90),
                'p95': np.percentile(token_counts, 95),
                'p99': np.percentile(token_counts, 99),
            },
            'char_stats': {
                'min': min(char_counts),
                'max': max(char_counts),
                'mean': np.mean(char_counts),
            },
            'ratio_stats': {
                'mean_chars_per_token': np.mean(ratios),
                'median_chars_per_token': np.median(ratios),
                'std_chars_per_token': np.std(ratios),
            },
            'raw_data': {
                'token_counts': token_counts,
                'char_counts': char_counts,
                'results': results
            }
        }
        
        return stats
    
    return {}

def print_analysis_results(stats: Dict[str, Any], model_type: str = ""):
    """
    Print formatted analysis results.
    """
    if not stats:
        print("No statistics available.")
        return
    
    print("\n" + "="*80)
    print("📊 EXACT TOKEN COUNT ANALYSIS")
    print("="*80)
    
    print(f"\n📈 Dataset Overview:")
    print(f"   Total samples: {stats['num_samples']}")
    
    print(f"\n🔤 Exact Token Statistics:")
    print("-"*40)
    t = stats['token_stats']
    print(f"  Min:        {t['min']:,} tokens")
    print(f"  Max:        {t['max']:,} tokens ⚠️")
    print(f"  Mean:       {t['mean']:,.0f} tokens")
    print(f"  Median:     {t['median']:,.0f} tokens")
    print(f"  Std Dev:    {t['std']:,.0f} tokens")
    print(f"  25th %ile:  {t['p25']:,.0f} tokens")
    print(f"  75th %ile:  {t['p75']:,.0f} tokens")
    print(f"  90th %ile:  {t['p90']:,.0f} tokens")
    print(f"  95th %ile:  {t['p95']:,.0f} tokens")
    print(f"  99th %ile:  {t['p99']:,.0f} tokens")
    
    print(f"\n📝 Character Statistics:")
    print("-"*40)
    c = stats['char_stats']
    print(f"  Min:        {c['min']:,} chars")
    print(f"  Max:        {c['max']:,} chars")
    print(f"  Mean:       {c['mean']:,.0f} chars")
    
    print(f"\n🔄 Tokenization Ratio:")
    print("-"*40)
    r = stats['ratio_stats']
    print(f"  Mean:       {r['mean_chars_per_token']:.2f} chars/token")
    print(f"  Median:     {r['median_chars_per_token']:.2f} chars/token")
    print(f"  Std Dev:    {r['std_chars_per_token']:.2f} chars/token")
    
    # Context length recommendations
    print(f"\n💡 Context Length Recommendations:")
    print("-"*40)
    
    context_sizes = [2048, 4096, 8192, 16384, 32768, 65536, 131072]
    token_counts = stats['raw_data']['token_counts']
    
    for ctx_size in context_sizes:
        over_limit = sum(1 for t in token_counts if t > ctx_size)
        percentage = (over_limit / len(token_counts)) * 100
        
        if percentage == 0:
            print(f"  ✅ {ctx_size:,} tokens: All samples fit (recommended)")
            break
        elif percentage < 1:
            print(f"  ⚠️  {ctx_size:,} tokens: {over_limit} samples ({percentage:.2f}%) exceed")
        else:
            print(f"  ❌ {ctx_size:,} tokens: {over_limit} samples ({percentage:.1f}%) exceed")
    
    # Memory estimation
    print(f"\n💾 Memory Estimation (per sample):")
    print("-"*40)
    max_tokens = t['max']
    p95_tokens = t['p95']
    
    # BF16 training memory estimation
    # Model weights + gradients + optimizer states + activations
    mem_per_token_mb = 0.003  # Rough estimate for 7B model
    
    print(f"  For max length ({max_tokens:,} tokens):")
    print(f"    ~{max_tokens * mem_per_token_mb:.1f} MB per sample")
    print(f"  For 95th percentile ({p95_tokens:.0f} tokens):")
    print(f"    ~{p95_tokens * mem_per_token_mb:.1f} MB per sample")

def plot_token_distribution(stats: Dict[str, Any], output_path: Optional[str] = None):
    """
    Create visualization of token distribution.
    """
    if not stats or 'raw_data' not in stats:
        print("No data to plot.")
        return
    
    token_counts = stats['raw_data']['token_counts']
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Exact Token Count Distribution', fontsize=16)
    
    # 1. Histogram
    ax1 = axes[0, 0]
    ax1.hist(token_counts, bins=30, edgecolor='black', alpha=0.7, color='blue')
    ax1.axvline(np.mean(token_counts), color='red', linestyle='--', 
                label=f'Mean: {np.mean(token_counts):.0f}')
    ax1.axvline(np.median(token_counts), color='green', linestyle='--', 
                label=f'Median: {np.median(token_counts):.0f}')
    ax1.set_xlabel('Token Count')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Token Count Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Cumulative distribution
    ax2 = axes[0, 1]
    sorted_tokens = sorted(token_counts)
    cumulative = np.arange(1, len(sorted_tokens) + 1) / len(sorted_tokens) * 100
    ax2.plot(sorted_tokens, cumulative, linewidth=2, color='blue')
    
    # Mark context sizes
    for ctx_size, color in [(4096, 'yellow'), (8192, 'orange'), (16384, 'red')]:
        if ctx_size <= max(sorted_tokens):
            ax2.axvline(ctx_size, color=color, linestyle=':', alpha=0.7, 
                       label=f'{ctx_size//1024}K context')
    
    ax2.set_xlabel('Token Count')
    ax2.set_ylabel('Cumulative Percentage (%)')
    ax2.set_title('Cumulative Distribution')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Box plot
    ax3 = axes[1, 0]
    bp = ax3.boxplot([token_counts], vert=False, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    ax3.set_xlabel('Token Count')
    ax3.set_title('Box Plot')
    ax3.grid(True, alpha=0.3)
    
    # 4. Statistics summary
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    stats_text = f"""
    Token Statistics:
    ─────────────────
    Samples: {len(token_counts)}
    Min: {min(token_counts):,}
    Max: {max(token_counts):,}
    Mean: {np.mean(token_counts):,.0f}
    Median: {np.median(token_counts):,.0f}
    Std Dev: {np.std(token_counts):,.0f}
    
    Percentiles:
    ─────────────────
    25th: {np.percentile(token_counts, 25):,.0f}
    75th: {np.percentile(token_counts, 75):,.0f}
    90th: {np.percentile(token_counts, 90):,.0f}
    95th: {np.percentile(token_counts, 95):,.0f}
    99th: {np.percentile(token_counts, 99):,.0f}
    """
    
    ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes,
             fontsize=11, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n📊 Plot saved to: {output_path}")
    
    plt.show()

def main():
    """
    Main function with examples for both Qwen and Llama.
    """
    parser = argparse.ArgumentParser(description='Exact token counter for LLM training data')
    parser.add_argument('--data_path', type=str, required=True, help='Path to JSONL data file')
    parser.add_argument('--model_path', type=str, required=True, help='Path to model/tokenizer')
    parser.add_argument('--model_type', type=str, choices=['qwen', 'llama', 'auto'], 
                       default='auto', help='Model type')
    parser.add_argument('--sample_size', type=int, default=None, 
                       help='Number of samples to analyze (default: all)')
    parser.add_argument('--plot', action='store_true', help='Generate visualization')
    parser.add_argument('--output_plot', type=str, default=None, help='Path to save plot')
    
    args = parser.parse_args()
    
    # Analyze dataset
    stats = analyze_dataset_with_tokenizer(
        jsonl_path=args.data_path,
        model_path=args.model_path,
        model_type=args.model_type,
        sample_size=args.sample_size
    )
    
    # Print results
    if stats:
        print_analysis_results(stats, args.model_type)
        
        # Generate plot if requested
        if args.plot:
            plot_token_distribution(stats, args.output_plot)
        
        # Save detailed results
        output_json = args.data_path.replace('.jsonl', '_token_analysis.json')
        with open(output_json, 'w') as f:
            # Save summary only (not raw data to avoid huge files)
            summary = {k: v for k, v in stats.items() if k != 'raw_data'}
            json.dump(summary, f, indent=2)
        print(f"\n📄 Detailed results saved to: {output_json}")

if __name__ == "__main__":
    # Example usage:
    # python exact_token_counter.py --data_path merged_training_data_qwen.jsonl --model_path Qwen/Qwen2.5-7B-Instruct --plot
    
    # Or run directly with hardcoded paths:
    if len(sys.argv) == 1:
        # Qwen analysis
        print("Running Qwen analysis...")
        stats_qwen = analyze_dataset_with_tokenizer(
            jsonl_path="/nas/ganluo/Flow_RL/training_data/training_data_raw_0825/filtered_simplified_transformed.jsonl",
            model_path="/nas/models/Qwen3-8B",  # 或本地路径
            model_type="qwen"
        )
        print_analysis_results(stats_qwen, "qwen")
        
        # Llama analysis  
        print("\n\nRunning Llama analysis...")
        stats_llama = analyze_dataset_with_tokenizer(
            jsonl_path="/nas/ganluo/Flow_RL/training_data/training_data_raw_0825/filtered_simplified_transformed.jsonl",
            model_path="/nas/models/Meta-Llama-3.1-8B-Instruct",  # 或本地路径
            model_type="llama"
        )
        print_analysis_results(stats_llama, "llama")
    else:
        main()