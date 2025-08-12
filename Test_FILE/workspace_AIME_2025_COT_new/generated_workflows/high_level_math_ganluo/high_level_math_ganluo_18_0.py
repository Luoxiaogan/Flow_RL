# Workflow ID: high_level_math_ganluo_18_0
# Benchmark: high_level_math_ganluo
# Data Indices: [6]

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
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio

        # Step 1: Extract key information and understand the problem
        extraction_instruction = (
            "Extract all numerical values, variables, relationships, and constraints from the problem. "
            "Identify the objective and any implicit assumptions. Organize this information clearly."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches
        approach_instructions = [
            f"Develop a combinatorial approach to solve the problem. Use the extracted information: {extracted_info}.",
            f"Develop an algebraic approach to solve the problem. Use the extracted information: {extracted_info}.",
            f"Develop a geometric or symmetry-based approach to solve the problem. Use the extracted information: {extracted_info}."
        ]
        approaches = await asyncio.gather(
            *[self.generate(instruction=instr, context=self.problem_text) for instr in approach_instructions]
        )

        # Step 3: Execute the approaches in parallel
        execution_instructions = [
            f"Follow this approach step-by-step to compute the solution: {approach}" for approach in approaches
        ]
        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=self.problem_text) for instr in execution_instructions]
        )

        # Step 4: Evaluate and select the best solution
        evaluation_instruction = (
            "Compare the candidate solutions, ensuring each satisfies all problem constraints. "
            "Select the most rigorous, complete, and mathematically sound solution. Resolve any inconsistencies."
        )
        final_solution = await self.ensemble(instruction=evaluation_instruction, contexts=candidate_solutions)

        # Step 5: Verify and refine the solution
        verification_instruction = (
            "Verify that the solution satisfies all problem constraints and conditions. "
            "Check for edge cases and ensure mathematical correctness. If necessary, refine the solution."
        )
        refined_solution = await self.revise(instruction=verification_instruction, context=final_solution)

        return refined_solution