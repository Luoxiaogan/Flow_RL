# Workflow ID: mbppplus_17_0
# Benchmark: mbppplus
# Data Indices: [18, 198, 220]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Phase 1: Problem Analysis & Rule Extraction
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the programming problem described. Identify:
1. The exact transformation or computation required.
2. Input and output data types and structures.
3. Key operations involved (e.g., filtering, rotating, merging).
4. Any implicit constraints or edge cases (empty inputs, boundary values, type preservation).
5. Expected behavior for edge cases even if not explicitly stated.
Provide a structured summary that can guide solution generation.""",
            context=""
        )

        # Phase 2: Generate Multiple Solution Candidates in Parallel
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the problem analysis:
{problem_analysis}

Generate a Python function that solves the problem. Use an imperative, step-by-step approach. 
- Include all necessary imports.
- Match the exact function signature from the problem.
- Handle edge cases explicitly.
- Return the correct data type.
Write ONLY the function implementation, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
{problem_analysis}

Generate a Python function that solves the problem using a functional or library-assisted approach (e.g., using comprehensions, itertools, or built-in methods). 
- Include all necessary imports.
- Match the exact function signature.
- Ensure robustness for edge cases.
- Return the correct data type.
Write ONLY the function implementation, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on the problem analysis:
{problem_analysis}

Generate a Python function that solves the problem with maximum efficiency and minimal code. 
- Include necessary imports.
- Use the most direct algorithm possible.
- Still handle all edge cases.
- Match function signature exactly.
Write ONLY the function implementation, no explanations.""",
                context=""
            )
        )

        # Phase 3: Generate Edge Cases and Validation Criteria
        edge_cases = await self.generate(
            instruction=f"""Based on the problem analysis:
{problem_analysis}

Generate a comprehensive list of edge cases and validation criteria for testing the solution. Include:
- Empty inputs
- Single-element inputs
- Boundary values
- Duplicates (if applicable)
- Type-specific edge cases (e.g., all digits in string, zero rotation, overlapping keys)
Format as a bulleted list with brief descriptions.""",
            context=""
        )

        # Phase 4: Validate and Revise Each Candidate
        revised_candidates = []
        for candidate in solution_candidates:
            validation_feedback = await self.generate(
                instruction=f"""Review the following solution candidate against the problem analysis and edge cases:

Problem Analysis:
{problem_analysis}

Edge Cases:
{edge_cases}

Candidate Solution:
{candidate}

Identify any flaws, missing edge case handling, incorrect return types, or inefficiencies. Provide specific, actionable feedback for improvement. If the solution is already correct and robust, state "APPROVED".""",
                context=candidate
            )
            
            if "APPROVED" not in validation_feedback.upper():
                revised_candidate = await self.revise(
                    instruction=f"""Revise the following solution based on the feedback below. Fix all identified issues while preserving the function signature and core logic.

Feedback:
{validation_feedback}

Original Solution:
{candidate}

Output ONLY the revised Python function implementation, no explanations.""",
                    context=candidate
                )
                revised_candidates.append(revised_candidate)
            else:
                revised_candidates.append(candidate)

        # Phase 5: Ensemble Selection of Best Solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below. Criteria:
1. Correctness: Must handle all edge cases and match expected behavior.
2. Robustness: Graceful handling of unexpected inputs.
3. Efficiency: Prefer simpler, faster implementations.
4. Code Clarity: Readable and maintainable.
5. Type Consistency: Returns exactly the expected type.

If multiple solutions are equally good, prefer the most concise one. Output ONLY the selected Python function implementation, nothing else.""",
            contexts_list=revised_candidates
        )

        return final_solution