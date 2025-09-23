# Workflow ID: mgsmbn_121_0
# Benchmark: mgsmbn
# Data Indices: [114]

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

        # Step 1: Classify problem type and complexity to adapt workflow depth
        classification = await self.generate(
            instruction="""Analyze this Bengali math problem and classify it:
            1. Problem Type: Is it percentage, rate, distribution, comparison, or multi-step?
            2. Complexity: Single-step (direct calculation) or Multi-step (requires intermediate values)?
            3. Entities: List all quantities, units, and relationships mentioned.
            4. Unknown: What is the final value being asked for?
            5. Constraints: Any real-world limits (whole numbers, positive values, etc.)?
            Format your response as a structured JSON-like summary.""",
            context=""
        )

        # Step 2: Hierarchical decomposition into subproblems with dependencies
        decomposition = await self.decompose(
            instruction=f"""Break this problem into minimal, solvable subproblems:
            - Each subproblem should be a single calculation or logical step
            - Explicitly state dependencies (which subproblems must be solved first)
            - Use clear variable names based on problem entities (e.g., 'remaining_cars', 'percentage_value')
            - Ensure the final subproblem directly yields the answer
            - Validate that dependencies form a directed acyclic graph
            Problem Classification: {classification}""",
            context=""
        )

        # Step 3: Revise decomposition for clarity and correctness
        revised_decomposition = await self.revise(
            instruction=f"""Improve this decomposition:
            - Fix any ambiguous or mathematically unsound subproblems
            - Ensure units are consistent across dependent steps
            - Add explicit formulas or relationships where missing
            - Verify that solving all subproblems in dependency order yields the final answer
            - Flag any potential edge cases (division by zero, negative quantities)
            Original Decomposition: {decomposition}""",
            context=str(decomposition)
        )

        # Step 4: Parallel solution generation - 3 different approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using step-by-step natural language reasoning:
                - Follow the revised decomposition exactly
                - Show all intermediate calculations with units
                - Explain each step in simple Bengali-math terms
                - Verify final answer against problem constraints
                Decomposition: {revised_decomposition}""",
                context=""
            ),
            self.programmer(
                instruction=f"""Solve using precise Python code:
                - Implement each subproblem as a separate calculation
                - Use descriptive variable names from decomposition
                - Include unit tracking in comments
                - Add assertions for constraints (e.g., assert result >= 0)
                - Return only the final numerical answer
                Decomposition: {revised_decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using algebraic modeling:
                - Define variables for unknowns
                - Set up equations based on relationships
                - Solve symbolically then substitute values
                - Show equation transformations step by step
                - Cross-validate with decomposition steps
                Decomposition: {revised_decomposition}""",
                context=""
            )
        )

        # Step 5: Ensemble synthesis - merge best elements from all attempts
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these attempts:
            - Prioritize numerical accuracy (match Programmer's result if valid)
            - Incorporate clear step-by-step explanations from natural language attempt
            - Use algebraic rigor where helpful for verification
            - Ensure units and constraints are properly handled
            - If attempts disagree, identify which has correct intermediate steps
            - Return ONLY the final numerical answer as a string (no units or text)""",
            contexts_list=solution_attempts
        )

        # Step 6: Iterative verification - sanity check the answer
        verification = await self.generate(
            instruction=f"""Verify this answer is correct and makes sense:
            - Plug the answer back into the original problem context
            - Check if it satisfies all given conditions
            - Ensure it meets real-world constraints (no negative cars, fractional people, etc.)
            - If error found, explain what went wrong
            Answer: {synthesized_solution}
            Problem: {self.problem_text}""",
            context=synthesized_solution
        )

        # Step 7: Final revision if verification fails
        if "error" in verification.lower() or "incorrect" in verification.lower():
            final_answer = await self.revise(
                instruction=f"""Correct the solution based on verification feedback:
                - Address the specific error identified
                - Recalculate using the most reliable method (prefer Programmer's approach)
                - Ensure all steps are mathematically sound
                - Return ONLY the corrected numerical answer
                Verification Feedback: {verification}
                Previous Answer: {synthesized_solution}""",
                context=synthesized_solution
            )
        else:
            final_answer = synthesized_solution

        # Clean and return final numerical answer
        # Extract only digits and decimal point
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (let evaluation handle)
            return final_answer.strip()