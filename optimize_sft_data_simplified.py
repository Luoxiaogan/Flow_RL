#!/usr/bin/env python3
"""
SFT Data Optimizer - Simplified Version
Optimizes SFT training data by:
1. Removing system prompts (shown to improve diversity)
2. Simplifying user prompts while keeping problem diversity
3. Converting code tags to markdown format
"""

import json
import re
import sys
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class SFTDataOptimizer:
    def __init__(self):
        """Initialize the optimizer with no predefined content templates."""
        pass

    def process_system_message(self, content: str) -> Optional[str]:
        """
        Remove system messages entirely from training data.
        Research shows training without system prompts but using them at inference
        improves both safety and diversity.
        """
        return None  # Completely remove system messages

    def process_user_message(self, content: str) -> str:
        """
        Reorganize user message to reduce repetition while maintaining task clarity.
        New structure:
        1. Problem Domain Overview
        2. Illustrative Examples (moved up for better flow)
        3. Core Operators (simplified)
        4. Meta-Learning Task & Guidelines
        5. Your Response
        """
        
        # Find key section boundaries in the original content
        section2_start = content.find("### 2. Available Operators")
        section6_start = content.find("### 6. Illustrative Example")
        section6_end = content.find("### 6. Your Response")
        
        # Handle cases where sections might not be found
        if section2_start == -1:
            print("Warning: Could not find '### 2. Available Operators'")
            return content
        if section6_start == -1:
            print("Warning: Could not find '### 6. Illustrative Example'")
            return content
        if section6_end == -1:
            # Try alternative endings
            section6_end = content.find("### 7.")
            if section6_end == -1:
                section6_end = len(content)
        
        # Extract the main content sections
        problem_overview = content[:section2_start].rstrip()
        examples_section = content[section6_start:section6_end].strip()
        ending_section = content[section6_end:].strip() if section6_end < len(content) else ""
        
        # Renumber sections for better flow
        examples_section = examples_section.replace("### 6. Illustrative Example", "### 2. Illustrative Example")
        ending_section = ending_section.replace("### 6. Your Response", "### 5. Your Response")
        
        # Build the simplified but complete middle section
        # This replaces the verbose operator descriptions with a concise version
        simplified_middle = """### 3. Core Operators

You have access to four fundamental operators, each pre-initialized with problem_text:
- **Generate(instruction: str, context: str = "") -> str**: Creates new content based on instructions
- **Revise(instruction: str, context: str) -> str**: Improves existing content
- **Summarize(instruction: str, context: str) -> str**: Condenses while preserving key information
- **Ensemble(instruction: str, contexts: List[str]) -> str**: Synthesizes multiple inputs

### 4. Meta-Learning Task & Implementation Guidelines

**Your Task:** Design a reusable Python workflow template that solves the entire problem CLASS, not specific instances. This is meta-learning - you're creating a system that learns patterns, not memorizing solutions.

**Key Guidelines:**
- Instructions should be comprehensive (100-500+ words when needed)
- Use f-strings for dynamic instruction construction
- Leverage asyncio.gather() for parallel operations
- Context parameter carries the actual data to process
- Never hardcode problem-specific information

**Response Format Required:**
1. A `<think>...</think>` block explaining your general solution strategy
2. A Python code block with the complete workflow implementation

**Template Structure:**
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # Pre-initialized operators - DO NOT MODIFY
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
    
    async def run_workflow(self):
        import asyncio
        # YOUR GENERIC WORKFLOW LOGIC HERE
        # Must work for ANY instance of this problem type
        pass
```"""
        
        # Combine all sections in the new order
        new_content = f"{problem_overview}\n\n{examples_section}\n\n{simplified_middle}\n\n{ending_section}"
        
        return new_content

    def process_assistant_message(self, content: str) -> str:
        """
        Convert <code> tags to markdown code blocks.
        This improves compatibility with modern LLM training formats.
        """
        # Replace <code> with ```python
        new_content = re.sub(r'<code>\s*', '\n```python\n', content)
        
        # Replace </code> with ```
        new_content = re.sub(r'\s*</code>', '\n```', new_content)
        
        return new_content

    def process_single_sample(self, sample: Dict) -> Dict:
        """
        Process a single training sample.
        Key changes:
        - Removes system messages entirely
        - Simplifies user messages
        - Converts code formatting in assistant messages
        """
        new_sample = sample.copy()
        new_messages = []
        
        for message in sample['messages']:
            role = message['role']
            
            if role == 'system':
                # Skip system messages entirely - don't add to new_messages
                processed_content = self.process_system_message(message['content'])
                if processed_content:  # Only add if not None (which it always will be)
                    new_message = message.copy()
                    new_message['content'] = processed_content
                    new_messages.append(new_message)
                # Since process_system_message returns None, this message is skipped
                
            elif role == 'user':
                # Process and add user message
                new_message = message.copy()
                new_message['content'] = self.process_user_message(message['content'])
                new_messages.append(new_message)
                
            elif role == 'assistant':
                # Process and add assistant message
                new_message = message.copy()
                new_message['content'] = self.process_assistant_message(message['content'])
                new_messages.append(new_message)
                
            else:
                # Keep any other role types unchanged (though there shouldn't be any)
                new_messages.append(message.copy())
        
        new_sample['messages'] = new_messages
        return new_sample

    def validate_sample(self, sample: Dict) -> List[str]:
        """
        Validate the processed sample format.
        Checks for:
        - Correct section structure in user messages
        - Proper formatting in assistant messages
        - Absence of system messages
        """
        issues = []
        
        # Check that no system messages remain
        if any(msg.get('role') == 'system' for msg in sample.get('messages', [])):
            issues.append("Sample still contains system message (should be removed)")
        
        for message in sample.get('messages', []):
            content = message.get('content', '')
            role = message.get('role', '')
            
            if role == 'assistant':
                # Check assistant message format
                if '<code>' in content or '</code>' in content:
                    issues.append("Assistant message still contains <code> tags")
                if '<think>' not in content or '</think>' not in content:
                    issues.append("Assistant message missing <think> tags")
                if '```python' not in content:
                    issues.append("Assistant message missing Python code block")
                    
            elif role == 'user':
                # Check for required sections in new structure
                required_sections = [
                    "### 1.",  # Problem Domain Overview
                    "### 2.",  # Illustrative Examples
                    "### 3.",  # Core Operators
                    "### 4.",  # Meta-Learning Task
                    "### 5."   # Your Response
                ]
                for section in required_sections:
                    if section not in content:
                        issues.append(f"User message missing section {section}")
        
        return issues

    def process_file(self, input_path: str, output_path: str, validate: bool = True) -> Tuple[int, int, Dict]:
        """
        Process an entire JSONL file of training samples.
        
        Args:
            input_path: Path to input JSONL file
            output_path: Path to output JSONL file
            validate: Whether to validate processed samples
            
        Returns:
            Tuple of (processed_count, error_count, validation_issues)
        """
        processed_count = 0
        error_count = 0
        validation_issues = {}
        
        # Ensure input file exists
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nProcessing: {input_path}")
        print(f"Output to: {output_path}")
        print("-" * 60)
        
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                if not line.strip():
                    continue
                
                try:
                    # Parse original data
                    sample = json.loads(line.strip())
                    
                    # Process the sample
                    new_sample = self.process_single_sample(sample)
                    
                    # Validate if requested
                    if validate:
                        issues = self.validate_sample(new_sample)
                        if issues:
                            validation_issues[f"Line {line_num}"] = issues
                    
                    # Write processed data
                    outfile.write(json.dumps(new_sample, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                    # Show progress
                    if processed_count % 100 == 0:
                        print(f"  Processed {processed_count} samples...")
                    
                except json.JSONDecodeError as e:
                    print(f"  Error: Invalid JSON at line {line_num}: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"  Error at line {line_num}: {e}")
                    error_count += 1
        
        return processed_count, error_count, validation_issues


def main():
    """Main entry point for the script."""
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Optimize SFT training data to improve diversity and reduce repetition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool optimizes SFT training data by:
1. Removing system prompts (improves diversity per research)
2. Simplifying repetitive user prompt sections
3. Converting code tags to markdown format
4. Preserving problem diversity (the key to good SFT)

Example usage:
  python optimize_sft_data_simplified.py input.jsonl output.jsonl
  python optimize_sft_data_simplified.py input.jsonl output.jsonl --no-validate
  
Based on research showing that:
- System prompts during training cause diversity collapse
- 1,000 diverse examples outperform 52,000 repetitive ones
- Cross-entropy loss reduces output diversity by up to 83%
        """
    )
    
    parser.add_argument(
        'input_path',
        type=str,
        help='Path to the input JSONL file'
    )
    
    parser.add_argument(
        'output_path',
        type=str,
        help='Path for the output JSONL file'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation of processed data'
    )
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Create optimizer instance
    optimizer = SFTDataOptimizer()
    
    # Execute processing
    try:
        print("\n" + "=" * 60)
        print("SFT Data Diversity Optimization Tool")
        print("=" * 60)
        
        processed, errors, issues = optimizer.process_file(
            input_path=args.input_path,
            output_path=args.output_path,
            validate=not args.no_validate
        )
        
        # Output statistics
        print("\n" + "=" * 60)
        print("Processing Summary")
        print("=" * 60)
        print(f"  Total processed: {processed} samples")
        print(f"  Total errors: {errors} samples")
        
        if processed + errors > 0:
            success_rate = (processed / (processed + errors)) * 100
            print(f"  Success rate: {success_rate:.2f}%")
        
        # Report validation issues if any
        if issues and not args.no_validate:
            print(f"\n  Validation issues found: {len(issues)} samples")
            # Show first 5 issues as examples
            for i, (location, sample_issues) in enumerate(list(issues.items())[:5]):
                print(f"\n  {location}:")
                for issue in sample_issues:
                    print(f"    - {issue}")
                if i == 4 and len(issues) > 5:
                    print(f"\n  ... and {len(issues) - 5} more samples with issues")
        elif not args.no_validate:
            print("\n  ✓ All samples passed validation!")
        
        # Final summary
        print("\n" + "=" * 60)
        if errors == 0 and (not issues or args.no_validate):
            print("Process completed successfully!")
            print("Your data should now have better diversity characteristics.")
        else:
            print("Process completed with some issues.")
            print("Please review the errors above.")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()