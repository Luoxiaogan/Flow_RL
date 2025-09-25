# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.verifier = operator.Verifier(self.llm, self.problem_text)
        self.refiner = operator.Refiner(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio

        # Step 1: Understand the problem deeply
        problem_analysis = await self.generate(
            instruction="""Carefully analyze the given mathematical problem and identify:
            1. The main question or goal
            2. Any constraints or conditions
            3. Key mathematical concepts or theorems that might be relevant
            4. Potential sub-problems or approaches to solving the problem
            Provide a clear, structured breakdown of these components.""",
            context=self.problem_text
        )

        # Step 2: Generate multiple solution approaches
        approach1 = await self.generate(
            instruction="""Given the problem statement and the detailed analysis:
            Develop a solution approach by breaking the problem into smaller, manageable parts.
            Focus on identifying the key steps required to solve the problem and justify each step with reasoning.
            Ensure that the approach is rigorous and mathematically sound.""",
            context=problem_analysis
        )

        approach2 = await self.generate(
            instruction="""Given the problem statement and the detailed analysis:
            Develop an alternative solution approach, possibly using different mathematical techniques or perspectives.
            Again, break the problem into sub-problems and justify each step with reasoning.
            Ensure that this approach is distinct from the first but equally rigorous and mathematically sound.""",
            context=problem_analysis
        )

        # Step 3: Ensemble decision between approaches
        selected_approach = await self.ensemble(
            instruction="""Evaluate the following two solution approaches:
            1. Approach 1: {approach1}
            2. Approach 2: {approach2}
            Select the best approach based on clarity, mathematical rigor, and completeness.
            Explain your reasoning for the selection decision.""",
            contexts=[approach1, approach2]
        )

        # Step 4: Generate the solution based on the selected approach
        solution = await self.generate(
            instruction=f"""Using the selected approach: {selected_approach}
            Construct a complete mathematical solution to the problem.
            Ensure that the solution includes:
            - A clear explanation of the reasoning process
            - All necessary steps and justifications
            - Proper formatting and notation
            - A final answer to the problem statement""",
            context=self.problem_text
        )

        # Step 5: Verify the solution
        verification = await self.verifier(
            instruction="""Carefully inspect the following solution for mathematical correctness:
            - Check for logical consistency and validity of all steps
            - Verify that all conditions and constraints are satisfied
            - Identify any gaps, errors, or ambiguities in the reasoning
            Provide a detailed report of your findings and verdict (valid/invalid/partial).""",
            context=solution
        )

        # Step 6: Refine the solution if necessary
        if verification['verdict'] != 'valid':
            refinement = await self.refiner(
                instruction=f"""Based on the following verification feedback: {verification}
                Improve the solution by addressing any identified issues or gaps.
                Ensure that the refined solution is mathematically rigorous and complete.""",
                context=solution,
                verification_feedback=str(verification)
            )
            refined_solution = refinement['refined_solution']
        else:
            refined_solution = solution

        return refined_solution