# Workflow ID: mbppplus_36_0
# Benchmark: mbppplus
# Data Indices: [332, 79]

import asyncio

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        import json

        # Phase 1: Parallel Problem Classification
        classification_instructions = [
            """Analyze the problem and classify its type based on INPUT/OUTPUT patterns:
            - What kind of input does it take? (string, list, number, etc.)
            - What kind of output does it produce?
            - What transformation or validation is being performed?
            - Identify keywords or operations暗示 (e.g., 'convert', 'check if', 'find', 'sort')
            Return a structured classification label like 'string_transformation', 'numerical_validation', etc.""",
            
            """Classify the problem by domain semantics:
            - Is it about text manipulation, mathematical logic, data structure operations, or boolean validation?
            - What common algorithms or Python constructs are likely needed? (regex, sorting, iteration, etc.)
            - Are there implied constraints or edge cases mentioned or hinted?
            Return a domain-based classification like 'text_regex', 'list_sorting', 'math_sequence', etc.""",
            
            """Classify by structural heuristics:
            - Does the problem require state tracking, cumulative operations, or pairwise comparisons?
            - Is order preservation important? Are duplicates relevant?
            - What would a brute-force vs. optimized solution look like?
            Return a structural classification like 'stateless_mapping', 'ordered_comparison', 'set_operation', etc."""
        ]

        classifications = await asyncio.gather(
            *[self.generate(instr, "") for instr in classification_instructions]
        )

        # Ensemble classifications into unified problem type
        problem_type = await self.ensemble(
            instruction="""Synthesize the three classification perspectives into one unified problem type descriptor.
            Resolve conflicts by majority or by choosing the most specific label.
            Format as a single concise label (e.g., 'string_case_conversion', 'monotonic_sequence_check').
            Also append a confidence score from 0-1 based on consensus strength.""",
            contexts_list=classifications
        )

        # Summarize problem type for downstream use
        problem_type_summary = await self.summarize(
            instruction="Extract only the final problem type label and confidence score. Ignore reasoning.",
            context=problem_type
        )

        # Phase 2: Strategy Generation with Edge-Case Revision Loop
        strategy = await self.generate(
            instruction=f"""Generate a detailed solution strategy for a problem of type: {problem_type_summary}.
            Include:
            - Step-by-step algorithmic plan (pseudocode acceptable)
            - Key edge cases to handle (empty inputs, single elements, duplicates, type boundaries)
            - Required Python constructs or libraries (e.g., 'use re for regex', 'use sorted() for comparison')
            - Expected input/output types and any conversion needed
            - Do NOT write actual code yet — focus on logic and structure.""",
            context=""
        )

        # Revise strategy for edge-case completeness (max 2 iterations)
        for _ in range(2):
            critique = await self.generate(
                instruction="""Critique the strategy for edge-case robustness:
                - Does it handle empty inputs?
                - Does it consider single-element cases?
                - Are type conversions or boundary conditions addressed?
                - Are there any assumptions that could break under stress?
                Return a list of missing edge cases or logical gaps.""",
                context=strategy
            )
            
            if "no issues" in critique.lower() or "none" in critique.lower():
                break
                
            strategy = await self.revise(
                instruction=f"""Revise the strategy to address these gaps: {critique}.
                Strengthen edge-case handling and remove any risky assumptions.
                Maintain the original structure but make it more defensive.""",
                context=strategy
            )

        # Phase 3: Code Generation with Parallel Validation
        code_draft = await self.programmer(
            instruction=f"""Implement the solution as a Python function.
            - Use the EXACT function signature from the problem.
            - Include all necessary imports at the top of the function body.
            - Handle all edge cases identified in the strategy.
            - Return the correct data type (list, tuple, string, bool, etc.) as implied by tests.
            - Write clean, readable code with meaningful variable names.
            Strategy to follow: {strategy}""",
            context=strategy,
            max_retries=3
        )

        # Generate 2 alternative implementations in parallel
        alt_instructions = [
            f"""Generate an alternative implementation using a DIFFERENT approach than the main draft.
            Main draft used: {strategy[:200]}...
            Try a more iterative/loop-based solution if the draft was functional, or vice versa.
            Still adhere to function signature and edge cases.""",
            
            f"""Generate an alternative implementation focusing on MAXIMAL ROBUSTNESS.
            Add explicit type checks, input validations, and verbose edge-case handling.
            Even if it's less elegant, prioritize correctness over brevity.
            Reference strategy: {strategy[:200]}..."""
        ]

        alt_codes = await asyncio.gather(
            *[self.programmer(instr, strategy, max_retries=2) for instr in alt_instructions]
        )

        # Ensemble final code by comparing outputs on synthetic edge cases
        final_code = await self.ensemble(
            instruction=f"""Select the best implementation from the three candidates.
            Criteria:
            1. Correctness on edge cases (empty, single, boundary)
            2. Adherence to expected return type
            3. Code clarity and maintainability
            4. Efficiency (avoid unnecessary operations)
            If all are good, prefer the most concise one.
            Return ONLY the selected code block, nothing else.""",
            contexts_list=[code_draft] + alt_codes
        )

        # Final cleanup: ensure no markdown, just pure code
        clean_code = await self.revise(
            instruction="Extract ONLY the Python function code. Remove any markdown, explanations, or extra text. Ensure imports are inside the function if required.",
            context=final_code
        )

        return clean_code