# Workflow ID: mbppplus_115_0
# Benchmark: mbppplus
# Data Indices: [71, 353]

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

        # PHASE 1: PROBLEM ASSESSMENT & CLASSIFICATION
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it:

1. Problem Type: Is this primarily mathematical, conditional, data transformation, or algorithmic?
2. Complexity Level: Trivial (single expression), Moderate (multiple branches), or Complex (nested logic)?
3. Edge Cases: What edge cases must be handled? (e.g., empty inputs, zeros, negatives, type mismatches)
4. Return Requirements: What exact return type is expected? Any special conditions (like returning None)?
5. Constraints: Are there any explicit or implicit constraints on inputs or outputs?

Format your response as a structured analysis with clear sections for each category above.""",
            context=""
        )

        # Determine strategy based on complexity
        strategy = "direct"
        if "complex" in classification.lower() or "moderate" in classification.lower():
            strategy = "decomposed"
        elif "ambiguous" in classification.lower() or "multiple approaches" in classification.lower():
            strategy = "parallel"

        # PHASE 2: STRATEGY EXECUTION
        if strategy == "direct":
            # Simple problems: go straight to code generation with rich context
            code_attempt = await self.programmer(
                instruction=f"""Generate a robust Python function that solves the problem. Consider:

Classification Context:
{classification}

Requirements:
- Match the exact function signature provided
- Handle all edge cases identified above
- Return correct data types (list vs tuple vs None)
- Include defensive checks if inputs might be invalid
- Prioritize clarity and correctness over brevity

Generate only the function implementation with necessary imports inside the function if needed.""",
                context=classification
            )
            final_code = code_attempt

        elif strategy == "decomposed":
            # Break down complex problems
            subproblems = await self.decompose(
                instruction=f"""Break this problem into minimal, independent subproblems:

Classification Context:
{classification}

Guidelines:
- Each subproblem should be solvable independently
- Order subproblems by dependency (if any)
- Focus on logical separation (input validation, core logic, edge handling, output formatting)
- Maximum 3-5 subproblems for efficiency""",
                context=classification
            )
            
            # Solve subproblems in parallel where possible
            subproblem_solutions = []
            for sp in subproblems:
                solution = await self.programmer(
                    instruction=f"""Solve this subproblem:

Subproblem: {sp['description']}

Overall Context:
{classification}

Requirements:
- Return only the code snippet or logic needed for this subproblem
- Assume inputs are pre-validated unless this subproblem handles validation
- Keep it minimal and focused""",
                    context=classification
                )
                subproblem_solutions.append(solution)
            
            # Synthesize final solution
            final_code = await self.generate(
                instruction=f"""Synthesize a complete solution from these subproblem solutions:

Classification: {classification}
Subproblem Solutions: {subproblem_solutions}

Requirements:
- Combine into a single coherent function
- Maintain proper variable names and flow
- Add any missing glue logic or error handling
- Ensure exact function signature match
- Return only the final function implementation""",
                context="\n".join(subproblem_solutions)
            )

        else:  # parallel strategy
            # Generate multiple solution approaches in parallel
            approaches = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate Solution Approach 1 (Direct Implementation):

Classification: {classification}

Focus on simplicity and direct translation of requirements to code.""",
                    context=classification
                ),
                self.programmer(
                    instruction=f"""Generate Solution Approach 2 (Defensive Programming):

Classification: {classification}

Focus on robustness: add input validation, handle edge cases explicitly, use clear conditionals.""",
                    context=classification
                ),
                self.programmer(
                    instruction=f"""Generate Solution Approach 3 (Optimized/Elegant):

Classification: {classification}

Focus on clean, pythonic code. Use built-ins and concise expressions where appropriate.""",
                    context=classification
                )
            )
            
            # Ensemble: select best approach
            final_code = await self.ensemble(
                instruction=f"""Select the best solution from these approaches:

Classification Context:
{classification}

Selection Criteria:
1. Correctness: Must handle all edge cases identified
2. Robustness: Defensive against invalid inputs
3. Clarity: Easy to understand and maintain
4. Conciseness: No unnecessary complexity
5. Type Safety: Returns exactly what's specified

Return ONLY the selected function implementation - no explanations.""",
                contexts_list=approaches
            )

        # PHASE 3: VALIDATION & HARDENING
        # Predict edge cases and harden code
        edge_case_analysis = await self.generate(
            instruction=f"""Predict potential edge cases and failure modes for this code:

Code:
{final_code}

Classification Context:
{classification}

Identify:
- Input scenarios that might break the code
- Type mismatches or boundary conditions
- Cases where return type might be wrong
- Any logical gaps in conditionals

Format as bullet points of specific test cases to consider.""",
            context=final_code
        )

        # Revise code to handle predicted edge cases
        hardened_code = await self.revise(
            instruction=f"""Improve this code to handle all predicted edge cases:

Edge Cases to Handle:
{edge_case_analysis}

Revision Requirements:
- Add necessary conditionals or type checks
- Ensure return types are always correct
- Maintain original function signature
- Keep code clean and readable
- Don't add unnecessary complexity

Return ONLY the revised function implementation.""",
            context=final_code
        )

        # Final cleanup: ensure pure function implementation (no extra text)
        clean_code = await self.generate(
            instruction="""Extract ONLY the Python function implementation from this text. Remove any explanations, markdown, or extra text. Return just the function code with necessary imports inside if needed.""",
            context=hardened_code
        )

        return clean_code