# Workflow ID: limr_67_0
# Benchmark: limr
# Data Indices: [303, 265]

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

        # Step 1: Deep Structural Analysis - Understand problem type, domain, and potential strategies
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this mathematical problem. Your analysis must include:
            1. Mathematical domain classification (e.g., number theory, combinatorics, algebra, geometry, optimization)
            2. Problem structure: Is it computational, proof-based, optimization, or construction?
            3. Key constraints and boundary conditions
            4. Potential solution strategies (list 2-3 approaches with brief rationale)
            5. Assessment of whether brute computation is feasible or if insight/transformation is required
            6. Any non-obvious symmetries, invariants, or transformations that could simplify the problem
            7. Expected answer format and range (remember: answer should be integer 000-999)
            Be thorough and precise. This analysis will guide all subsequent steps.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration - Run decomposition and creative insight generation concurrently
        decomposition_task = self.decompose(
            instruction="""Break this problem down into a sequence of logical subproblems. For each subproblem:
            - Clearly state what needs to be solved
            - Identify any mathematical tools or theorems required
            - Specify dependencies on other subproblems
            - Estimate complexity (low/medium/high)
            Structure the output as a dependency graph of subproblems.""",
            context=problem_analysis
        )

        creative_insight_task = self.generate(
            instruction=f"""Based on the problem analysis: {problem_analysis[:1000]}
            Generate 3-5 non-obvious insights, transformations, or substitutions that could radically simplify this problem.
            Examples: 
            - Recognizing a hidden symmetry or invariant
            - Applying a clever substitution (e.g., trigonometric, modular, combinatorial)
            - Transforming the problem into a different domain (e.g., geometric to algebraic)
            - Identifying a known theorem or identity that applies
            - Spotting a pattern or recurrence that wasn't immediately obvious
            For each insight, explain why it's powerful and how it changes the problem's complexity.""",
            context=problem_analysis
        )

        # Execute both tasks in parallel
        decomposition_result, creative_insights = await asyncio.gather(decomposition_task, creative_insight_task)

        # Step 3: Strategy Synthesis - Combine decomposition and creative insights into unified solution roadmap
        solution_roadmap = await self.ensemble(
            instruction="""Synthesize the structured decomposition and creative insights into a coherent solution strategy. Your synthesis must:
            1. Prioritize approaches based on elegance and efficiency
            2. Resolve any conflicts between decomposition steps and creative insights
            3. Create a step-by-step plan that leverages the best of both structured and creative approaches
            4. Flag any high-risk steps that may require verification
            5. Decide whether the primary solution method should be computational (code) or analytical (proof/reasoning)
            Output a clear, numbered solution roadmap with estimated confidence for each step.""",
            contexts_list=[str(decomposition_result), creative_insights]
        )

        # Step 4: Conditional Execution - Route to appropriate solving method based on roadmap
        if "computational" in solution_roadmap.lower() or "code" in solution_roadmap.lower() or "program" in solution_roadmap.lower():
            # Computational path
            code_solution = await self.programmer(
                instruction=f"""Based on this solution roadmap: {solution_roadmap[:1500]}
                Write Python code to solve the problem. Requirements:
                - Include detailed comments explaining each step
                - Handle edge cases and boundary conditions
                - Optimize for correctness over speed
                - Return the final answer as an integer between 000 and 999
                - If multiple answers, sum them; if none, return 000
                Verify your code with at least one test case if possible.""",
                context=solution_roadmap
            )
            raw_solution = code_solution
        else:
            # Analytical path - Generate and iteratively refine a proof/solution
            analytical_solution = await self.generate(
                instruction=f"""Based on this solution roadmap: {solution_roadmap[:1500]}
                Develop a complete, rigorous solution. Requirements:
                - Show all mathematical steps clearly
                - Justify each non-trivial step
                - Use proper mathematical notation
                - Conclude with a boxed final answer (integer 000-999)
                - If multiple answers, sum them; if none, return 000""",
                context=solution_roadmap
            )
            
            # Iterative refinement loop (max 3 iterations)
            current_solution = analytical_solution
            for i in range(3):
                validation = await self.generate(
                    instruction=f"""Critically review this solution for:
                    1. Logical gaps or errors
                    2. Missing edge cases
                    3. Calculation mistakes
                    4. Clarity and rigor
                    If no significant issues, respond with 'VALIDATED'. Otherwise, list specific issues.""",
                    context=current_solution
                )
                
                if "VALIDATED" in validation or "no significant issues" in validation.lower():
                    break
                else:
                    current_solution = await self.revise(
                        instruction=f"""Revise the solution to address these issues: {validation[:1000]}
                        Maintain mathematical rigor and clarity. Ensure final answer is an integer 000-999.""",
                        context=current_solution
                    )
            raw_solution = current_solution

        # Step 5: Adversarial Validation - Try to break the solution
        adversarial_check = await self.generate(
            instruction=f"""Play devil's advocate. Assume this solution is wrong: {raw_solution[:1500]}
            What is the most plausible point of failure? Consider:
            - Edge cases not considered
            - Mathematical assumptions that might not hold
            - Calculation errors in complex steps
            - Misinterpretation of the original problem
            If you find a credible flaw, describe it precisely. Otherwise, state 'NO FLAWS FOUND'.""",
            context=raw_solution
        )

        # If flaws found, trigger one revision
        if "NO FLAWS FOUND" not in adversarial_check and "no credible flaw" not in adversarial_check.lower():
            final_solution = await self.revise(
                instruction=f"""Address this potential flaw: {adversarial_check[:1000]}
                Revise the solution while preserving its core approach. Ensure final answer is an integer 000-999.""",
                context=raw_solution
            )
        else:
            final_solution = raw_solution

        # Step 6: Final Answer Extraction - Ensure proper format
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from this solution: {final_solution[:2000]}
            Requirements:
            - Answer must be an integer between 000 and 999
            - If multiple valid answers, sum them
            - If no answer found, return 000
            - Output ONLY the 3-digit number (e.g., '123', '007', '000')
            - No explanations, no units, no text""",
            context=final_solution
        )

        # Clean and validate final answer format
        # Extract first 3-digit number from response
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: try to extract any number and format to 3 digits
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                return "000"