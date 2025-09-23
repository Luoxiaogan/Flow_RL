# Workflow ID: mbppplus_19_0
# Benchmark: mbppplus
# Data Indices: [8, 136, 329]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for algorithmic programming problems.
        Uses meta-reflective diamond cascade: classify → parallel solve → validate → revise → ensemble.
        """
        import asyncio
        import re

        # PHASE 1: Problem Decomposition & Classification
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Output in EXACTLY this format:

CLASSIFICATION: [numerical|textual_regex|logical|other]
CONSTRAINTS: [bullet-point list of explicit/implicit constraints]
EDGE_CASES: [bullet-point list of potential edge cases: empty inputs, zeros, negatives, duplicates, etc.]
RETURN_TYPE: [specify expected return type: int, str, list, tuple, etc.]
KEY_OPERATIONS: [list core operations needed: e.g., floor division, regex match, set intersection]

Be exhaustive. Think like a test case designer trying to break the solution.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (Diamond Fork)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct, minimal solution based on problem analysis:
{problem_analysis}

Follow these rules:
- Use EXACT function signature from problem
- Handle ALL edge cases mentioned in analysis
- Return correct type as specified
- Prioritize readability and efficiency
- Include necessary imports INSIDE function if needed
- Output ONLY the function code, no explanations""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate an alternative solution using a different approach:
{problem_analysis}

Example alternatives:
- If direct math, try iterative or recursive
- If regex, try manual string parsing
- If set operations, try list comprehensions

Same output rules: ONLY function code, correct signature, handle edge cases, proper return type.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a defensive, ultra-robust solution:
{problem_analysis}

Assume inputs are malicious. Add explicit type checks, boundary validations, and fallback behaviors.
Still must match exact function signature and return type.
Output ONLY the function code.""",
                context=problem_analysis
            )
        )

        # PHASE 3: Adversarial Validation (Parallel)
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Critically validate this solution against problem requirements and edge cases:

PROBLEM ANALYSIS:
{problem_analysis}

SOLUTION ATTEMPT:
{attempt}

Check:
1. Does it handle ALL edge cases listed?
2. Is return type correct?
3. Does it match function signature exactly?
4. Any off-by-one errors or type mismatches?
5. Would it pass the sample test cases?

Output format:
VALID: [yes|no]
ISSUES: [bullet-point list of specific flaws, if any]
CONFIDENCE: [high|medium|low]""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # PHASE 4: Conditional Revision Loop (Max 2 iterations)
        refined_solutions = []
        for i, (attempt, validation) in enumerate(zip(solution_attempts, validations)):
            current_solution = attempt
            current_validation = validation
            
            for revision_round in range(2):  # Max 2 revisions
                if "VALID: yes" in current_validation and "CONFIDENCE: high" in current_validation:
                    break  # Early exit if confident and valid
                    
                # Revise based on validation feedback
                current_solution = await self.revise(
                    instruction=f"""Fix ALL issues identified in validation:

VALIDATION FEEDBACK:
{current_validation}

PROBLEM CONTEXT:
{problem_analysis}

Requirements:
- Preserve exact function signature
- Fix identified flaws while maintaining core logic
- Still handle all edge cases
- Output ONLY the corrected function code""",
                    context=current_solution
                )
                
                # Re-validate
                current_validation = await self.generate(
                    instruction=f"""Re-validate this revised solution:

PROBLEM ANALYSIS:
{problem_analysis}

REVISED SOLUTION:
{current_solution}

Same validation criteria as before.
Output format:
VALID: [yes|no]
ISSUES: [bullet-point list]
CONFIDENCE: [high|medium|low]""",
                    context=current_solution
                )
            
            refined_solutions.append(current_solution)

        # PHASE 5: Ensemble with Metadata (Diamond Merge)
        final_selection = await self.ensemble(
            instruction="""Select the BEST solution using this criteria:

1. Correctness: Must handle all edge cases and match signature
2. Simplicity: Prefer minimal, readable code over complex robustness
3. Efficiency: Avoid unnecessary computations
4. Confidence: Prioritize solutions with "VALID: yes" and "CONFIDENCE: high"

If multiple solutions are equally good, choose the most elegant.
Output ONLY the selected function code - no explanations, no markdown.

CRITICAL: The output must be executable Python code that solves the original problem.""",
            contexts_list=refined_solutions
        )

        return final_selection