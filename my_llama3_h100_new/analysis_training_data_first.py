#!/usr/bin/env python3
"""
Analyze the length distribution of training data in JSONL format.
Counts English letters/characters (not tokens) for each conversation.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
from collections import Counter

def count_message_length(messages: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Count the character length of messages.
    
    Returns:
        Dictionary with length statistics for each role and total
    """
    stats = {
        'system': 0,
        'user': 0,
        'assistant': 0,
        'total': 0,
        'num_turns': 0,
        'num_messages': len(messages)
    }
    
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        char_count = len(content)
        
        if role in stats:
            stats[role] += char_count
        stats['total'] += char_count
        
        # Count conversation turns (user-assistant pairs)
        if role == 'user':
            stats['num_turns'] += 1
    
    return stats

def analyze_jsonl_file(filepath: str) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Analyze a JSONL file and return length statistics.
    
    Returns:
        Tuple of (list of individual stats, aggregated stats)
    """
    if not Path(filepath).exists():
        print(f"Error: File not found - {filepath}")
        return [], {}
    
    individual_stats = []
    total_samples = 0
    
    print(f"\nAnalyzing: {filepath}")
    print("=" * 80)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            try:
                data = json.loads(line)
                messages = data.get('messages', [])
                
                # Count lengths
                stats = count_message_length(messages)
                stats['line_num'] = line_num
                
                # Add metadata if available
                if 'workflow_id' in data:
                    stats['workflow_id'] = data['workflow_id']
                if 'benchmark' in data:
                    stats['benchmark'] = data['benchmark']
                
                individual_stats.append(stats)
                total_samples += 1
                
                # Print progress every 100 samples
                if line_num % 100 == 0:
                    print(f"  Processed {line_num} samples...", end='\r')
                    
            except json.JSONDecodeError as e:
                print(f"  Warning: Invalid JSON at line {line_num}: {e}")
                continue
    
    print(f"  Processed {total_samples} samples total.    ")
    
    # Calculate aggregate statistics
    if individual_stats:
        lengths = [s['total'] for s in individual_stats]
        system_lengths = [s['system'] for s in individual_stats]
        user_lengths = [s['user'] for s in individual_stats]
        assistant_lengths = [s['assistant'] for s in individual_stats]
        num_turns = [s['num_turns'] for s in individual_stats]
        
        aggregate_stats = {
            'total_samples': total_samples,
            'length_stats': {
                'min': min(lengths),
                'max': max(lengths),
                'mean': np.mean(lengths),
                'median': np.median(lengths),
                'std': np.std(lengths),
                'p25': np.percentile(lengths, 25),
                'p75': np.percentile(lengths, 75),
                'p90': np.percentile(lengths, 90),
                'p95': np.percentile(lengths, 95),
                'p99': np.percentile(lengths, 99),
            },
            'role_stats': {
                'system': {
                    'mean': np.mean(system_lengths),
                    'max': max(system_lengths),
                    'total': sum(system_lengths)
                },
                'user': {
                    'mean': np.mean(user_lengths),
                    'max': max(user_lengths),
                    'total': sum(user_lengths)
                },
                'assistant': {
                    'mean': np.mean(assistant_lengths),
                    'max': max(assistant_lengths),
                    'total': sum(assistant_lengths)
                }
            },
            'turn_stats': {
                'mean_turns': np.mean(num_turns),
                'max_turns': max(num_turns),
                'min_turns': min(num_turns)
            },
            'lengths': lengths
        }
        
        # Benchmark distribution if available
        benchmarks = [s.get('benchmark', 'unknown') for s in individual_stats]
        aggregate_stats['benchmark_distribution'] = Counter(benchmarks)
        
    else:
        aggregate_stats = {}
    
    return individual_stats, aggregate_stats

def estimate_token_count(char_count: int, model_type: str = 'general') -> int:
    """
    Rough estimation of token count from character count.
    
    For English text:
    - GPT/Llama models: roughly 1 token per 4 characters
    - Chinese text: roughly 1 token per 2 characters
    """
    if model_type in ['qwen', 'llama', 'general']:
        # For English text, roughly 1 token per 4 characters
        # This is a rough approximation
        return int(char_count / 4)
    return int(char_count / 4)

def print_statistics(stats: Dict[str, Any], model_type: str = 'general'):
    """Print formatted statistics."""
    
    if not stats:
        print("No statistics available.")
        return
    
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    print(f"\nTotal samples: {stats['total_samples']}")
    
    print("\n📊 Character Length Distribution:")
    print("-" * 40)
    length_stats = stats['length_stats']
    print(f"  Min:        {length_stats['min']:,} chars")
    print(f"  Max:        {length_stats['max']:,} chars")
    print(f"  Mean:       {length_stats['mean']:,.0f} chars")
    print(f"  Median:     {length_stats['median']:,.0f} chars")
    print(f"  Std Dev:    {length_stats['std']:,.0f} chars")
    print(f"  25th %ile:  {length_stats['p25']:,.0f} chars")
    print(f"  75th %ile:  {length_stats['p75']:,.0f} chars")
    print(f"  90th %ile:  {length_stats['p90']:,.0f} chars")
    print(f"  95th %ile:  {length_stats['p95']:,.0f} chars")
    print(f"  99th %ile:  {length_stats['p99']:,.0f} chars")
    
    print("\n🔤 Estimated Token Counts (rough approximation):")
    print("-" * 40)
    print(f"  Mean:       ~{estimate_token_count(length_stats['mean'], model_type):,} tokens")
    print(f"  Median:     ~{estimate_token_count(length_stats['median'], model_type):,} tokens")
    print(f"  95th %ile:  ~{estimate_token_count(length_stats['p95'], model_type):,} tokens")
    print(f"  99th %ile:  ~{estimate_token_count(length_stats['p99'], model_type):,} tokens")
    print(f"  Max:        ~{estimate_token_count(length_stats['max'], model_type):,} tokens")
    
    print("\n👥 Role-based Statistics:")
    print("-" * 40)
    for role in ['system', 'user', 'assistant']:
        role_stat = stats['role_stats'][role]
        print(f"  {role.capitalize()}:")
        print(f"    Mean length: {role_stat['mean']:,.0f} chars")
        print(f"    Max length:  {role_stat['max']:,} chars")
    
    print("\n💬 Conversation Statistics:")
    print("-" * 40)
    turn_stats = stats['turn_stats']
    print(f"  Mean turns:  {turn_stats['mean_turns']:.1f}")
    print(f"  Min turns:   {turn_stats['min_turns']}")
    print(f"  Max turns:   {turn_stats['max_turns']}")
    
    if 'benchmark_distribution' in stats:
        print("\n📚 Benchmark Distribution:")
        print("-" * 40)
        for benchmark, count in stats['benchmark_distribution'].most_common():
            percentage = (count / stats['total_samples']) * 100
            print(f"  {benchmark}: {count} ({percentage:.1f}%)")
    
    # Context length warnings
    print("\n⚠️  Context Length Considerations:")
    print("-" * 40)
    
    # Different context limits (in estimated tokens)
    context_limits = {
        '4K context': 4096,
        '8K context': 8192,
        '32K context': 32768,
        '128K context': 131072
    }
    
    lengths = stats['lengths']
    for context_name, token_limit in context_limits.items():
        char_limit = token_limit * 4  # Rough conversion back to characters
        over_limit = sum(1 for l in lengths if l > char_limit)
        percentage = (over_limit / len(lengths)) * 100
        
        if percentage > 0:
            print(f"  {context_name} ({token_limit:,} tokens):")
            print(f"    {over_limit} samples ({percentage:.2f}%) exceed this limit")

def plot_distribution(stats: Dict[str, Any], output_path: str = None):
    """Create visualization of length distribution."""
    
    if not stats or 'lengths' not in stats:
        print("No data to plot.")
        return
    
    lengths = stats['lengths']
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Training Data Length Distribution Analysis', fontsize=16)
    
    # 1. Histogram of character lengths
    ax1 = axes[0, 0]
    ax1.hist(lengths, bins=50, edgecolor='black', alpha=0.7)
    ax1.axvline(np.mean(lengths), color='red', linestyle='--', label=f'Mean: {np.mean(lengths):.0f}')
    ax1.axvline(np.median(lengths), color='green', linestyle='--', label=f'Median: {np.median(lengths):.0f}')
    ax1.set_xlabel('Character Count')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Character Length Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Histogram of estimated token lengths
    ax2 = axes[0, 1]
    token_lengths = [estimate_token_count(l) for l in lengths]
    ax2.hist(token_lengths, bins=50, edgecolor='black', alpha=0.7, color='orange')
    ax2.axvline(np.mean(token_lengths), color='red', linestyle='--', label=f'Mean: {np.mean(token_lengths):.0f}')
    ax2.axvline(np.median(token_lengths), color='green', linestyle='--', label=f'Median: {np.median(token_lengths):.0f}')
    ax2.set_xlabel('Estimated Token Count')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Estimated Token Distribution (1 token ≈ 4 chars)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Cumulative distribution
    ax3 = axes[1, 0]
    sorted_lengths = sorted(lengths)
    cumulative = np.arange(1, len(sorted_lengths) + 1) / len(sorted_lengths) * 100
    ax3.plot(sorted_lengths, cumulative, linewidth=2)
    
    # Mark context length limits
    context_limits = [
        (4096 * 4, '4K'),
        (8192 * 4, '8K'),
        (32768 * 4, '32K'),
        (131072 * 4, '128K')
    ]
    
    for limit, label in context_limits:
        if limit <= max(sorted_lengths):
            ax3.axvline(limit, color='red', linestyle=':', alpha=0.5, label=f'{label} context')
    
    ax3.set_xlabel('Character Count')
    ax3.set_ylabel('Cumulative Percentage (%)')
    ax3.set_title('Cumulative Distribution Function')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. Box plot
    ax4 = axes[1, 1]
    box_data = [lengths]
    bp = ax4.boxplot(box_data, labels=['All Samples'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    ax4.set_ylabel('Character Count')
    ax4.set_title('Box Plot of Length Distribution')
    ax4.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f"Samples: {len(lengths)}\n"
    stats_text += f"Mean: {np.mean(lengths):.0f}\n"
    stats_text += f"Median: {np.median(lengths):.0f}\n"
    stats_text += f"Std: {np.std(lengths):.0f}\n"
    stats_text += f"Max: {max(lengths):.0f}"
    ax4.text(0.02, 0.98, stats_text, transform=ax4.transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved to: {output_path}")
    
    plt.show()

def main():
    """Main function to analyze both Qwen and Llama datasets."""
    
    base_dir = "/Users/luogan/Code/workflow_generation/Flow_RL/training_data/0807_SFT_没有filter就合并"
    
    files_to_analyze = [
        # {
        #     'path': f"{base_dir}/merged_training_data_qwen.jsonl",
        #     'model': 'qwen',
        #     'name': 'Qwen-2.5-7B Training Data'
        # },
        {
            'path': f"{base_dir}/merged_training_data_llama.jsonl",
            'model': 'llama',
            'name': 'Llama-3.1-8B Training Data'
        }
    ]
    
    all_results = {}
    
    for file_info in files_to_analyze:
        filepath = file_info['path']
        model_type = file_info['model']
        name = file_info['name']
        
        print("\n" + "="*80)
        print(f"📝 {name}")
        print("="*80)
        
        if not Path(filepath).exists():
            print(f"⚠️  File not found: {filepath}")
            continue
        
        # Get file size
        file_size = Path(filepath).stat().st_size / (1024 * 1024)  # Size in MB
        print(f"File size: {file_size:.2f} MB")
        
        # Analyze the file
        individual_stats, aggregate_stats = analyze_jsonl_file(filepath)
        
        if aggregate_stats:
            all_results[model_type] = {
                'individual': individual_stats,
                'aggregate': aggregate_stats,
                'name': name
            }
            
            # Print statistics
            print_statistics(aggregate_stats, model_type)
            
            # Create plot
            plot_output = f"{base_dir}/{model_type}_length_distribution.png"
            plot_distribution(aggregate_stats, plot_output)
    
    # Compare both datasets
    if len(all_results) == 2:
        print("\n" + "="*80)
        print("📊 COMPARISON BETWEEN QWEN AND LLAMA DATASETS")
        print("="*80)
        
        qwen_stats = all_results.get('qwen', {}).get('aggregate', {})
        llama_stats = all_results.get('llama', {}).get('aggregate', {})
        
        if qwen_stats and llama_stats:
            print("\n📈 Dataset Size:")
            print(f"  Qwen:  {qwen_stats['total_samples']} samples")
            print(f"  Llama: {llama_stats['total_samples']} samples")
            
            print("\n📏 Mean Length:")
            print(f"  Qwen:  {qwen_stats['length_stats']['mean']:,.0f} chars")
            print(f"  Llama: {llama_stats['length_stats']['mean']:,.0f} chars")
            
            print("\n📊 Max Length:")
            print(f"  Qwen:  {qwen_stats['length_stats']['max']:,} chars")
            print(f"  Llama: {llama_stats['length_stats']['max']:,} chars")
            
            # Check if they're the same (should be if conversion was correct)
            if qwen_stats['total_samples'] == llama_stats['total_samples']:
                print("\n✅ Both datasets have the same number of samples (as expected)")
            else:
                print("\n⚠️  Warning: Datasets have different sample counts!")
    
    # Recommendations
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    for model_type, results in all_results.items():
        stats = results['aggregate']
        name = results['name']
        
        print(f"\n{name}:")
        
        # Recommend max_seq_length based on percentiles
        p95_tokens = estimate_token_count(stats['length_stats']['p95'], model_type)
        p99_tokens = estimate_token_count(stats['length_stats']['p99'], model_type)
        max_tokens = estimate_token_count(stats['length_stats']['max'], model_type)
        
        # Suggest practical max_seq_length values
        if p99_tokens <= 2048:
            suggested = 2048
        elif p99_tokens <= 4096:
            suggested = 4096
        elif p99_tokens <= 8192:
            suggested = 8192
        elif p99_tokens <= 16384:
            suggested = 16384
        elif p99_tokens <= 32768:
            suggested = 32768
        else:
            suggested = 65536
        
        print(f"  Suggested max_seq_length: {suggested:,} tokens")
        print(f"    - Covers 99% of data (p99: ~{p99_tokens:,} tokens)")
        print(f"    - Max sample needs: ~{max_tokens:,} tokens")
        
        # Memory considerations
        memory_per_sample_gb = (suggested * 2 * 4) / (1024**3)  # bf16, with gradients
        print(f"  Estimated memory per sample: ~{memory_per_sample_gb:.2f} GB")
        print(f"  With batch_size=4: ~{memory_per_sample_gb * 4:.2f} GB")

if __name__ == "__main__":
    main()