# Workflow ID: limr_63_0
# Benchmark: limr
# Data Indices: [156, 327]

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

        # Step 1: Meta-classification - Understand the problem type and required strategies
        classification = await self.generate(
            instruction="""Perform a deep meta-analysis of this mathematical problem:
            1. Classify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Identify the core question: What exactly is being asked? Extract the target (e.g., minimal degree, units digit, count, etc.)
            3. Determine the solution approach: Is this primarily computational, theoretical, or hybrid?
            4. List relevant mathematical principles (e.g., conjugate root theorem, modular arithmetic, generating functions, etc.)
            5. Predict potential pitfalls or non-obvious insights required.
            6. Recommend 2-3 distinct solution strategies.
            Format your response as a structured analysis with clear section headings.""",
            context=""
        )

        # Step 2: Conditional branching based on classification
        if "computational" in classification.lower() and ("digit" in classification.lower() or "sum" in classification.lower()):
            # Direct computational path
            solution_attempt = await self.generate(
                instruction=f"""Based on the classification:
                {classification}
                
                Generate a precise, step-by-step computational solution. Focus on:
                - Exact arithmetic (no approximations)
                - Modular arithmetic if applicable
                - Handling of large numbers via patterns or cycles
                - Clear final answer extraction
                Show all steps but keep it concise.""",
                context=classification
            )
            
            # Validate with programmer
            code_solution = await self.programmer(
                instruction=f"""Write a Python script that computes the exact answer to this problem.
                The script must:
                - Handle all edge cases mentioned in the problem
                - Use only standard libraries
                - Output only the final integer answer (0-999)
                - Include comments explaining key steps
                Base your code on this analysis: {solution_attempt}""",
                context=solution_attempt
            )
            
            # Final revision for answer formatting
            final_answer = await self.revise(
                instruction="""Extract the final numerical answer from the solution. 
                Ensure it is an integer between 0 and 999. 
                If the answer is not in this range, apply modulo 1000 or select the smallest non-negative valid answer.
                Return ONLY the 3-digit formatted answer (e.g., '007', '123', '000').""",
                context=code_solution
            )
            
        else:
            # Complex theoretical path - use Diamond Pattern + Cascade
            # Generate multiple perspectives
            perspectives = await asyncio.gather(
                self.generate(
                    instruction=f"""Adopt a pure theoretical approach:
                    {classification}
                    Derive the solution using formal mathematical reasoning, theorems, and proofs.
                    Focus on elegance and theoretical soundness. Ignore computation.""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Adopt a computational verification approach:
                    {classification}
                    Even if theoretical, find a way to verify or approximate the answer computationally.
                    Use bounds, examples, or algorithmic construction.""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Adopt an edge-case and counterexample approach:
                    {classification}
                    What are the boundary conditions? What if assumptions are violated?
                    How does the answer change under perturbation? Use this to validate or refine.""",
                    context=classification
                )
            )
            
            # Summarize each perspective
            summaries = await asyncio.gather(
                *[self.summarize(
                    instruction="Extract the core argument, key mathematical principle, and final answer. Omit derivations.",
                    context=p
                ) for p in perspectives]
            )
            
            # Ensemble synthesis
            synthesized = await self.ensemble(
                instruction="""Synthesize the best solution from these perspectives:
                - Prefer theoretically sound answers that are computationally verified
                - If answers conflict, identify the most rigorous and consistent one
                - Ensure the answer is an integer between 0 and 999
                - Explain why you selected this answer over others""",
                contexts_list=summaries
            )
            
            # Iterative refinement loop (max 2 iterations)
            current_solution = synthesized
            for i in range(2):
                critique = await self.generate(
                    instruction=f"""Critique this solution:
                    {current_solution}
                    Check for:
                    - Logical consistency
                    - Mathematical correctness
                    - Adherence to problem constraints
                    - Answer format (integer 0-999)
                    If no issues, respond 'VALID'. Otherwise, list specific errors.""",
                    context=current_solution
                )
                
                if "VALID" in critique.upper():
                    break
                else:
                    current_solution = await self.revise(
                        instruction=f"""Fix the following issues:
                        {critique}
                        Maintain the original solution's strengths while correcting errors.
                        Ensure final answer is an integer 0-999.""",
                        context=current_solution
                    )
            
            # Final answer extraction
            final_answer = await self.revise(
                instruction="""Extract the final numerical answer. 
                Ensure it is an integer between 0 and 999. 
                Format as exactly 3 digits with leading zeros if needed (e.g., '007', '123', '000').
                Return ONLY this 3-digit string.""",
                context=current_solution
            )

        # Safety: Ensure 3-digit format
        # Extract digits only
        digits = re.sub(r'\D', '', final_answer)
        if len(digits) == 0:
            digits = "000"
        elif len(digits) > 3:
            digits = digits[-3:]  # Take last 3 digits
        elif len(digits) < 3:
            digits = digits.zfill(3)
        
        return digits