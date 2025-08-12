# Workflow ID: high_level_math_ganluo_3_0
# Benchmark: high_level_math_ganluo
# Data Indices: [12]

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

        # Step 1: Extract critical components of the problem
        extraction_instruction = (
            "Extract all numerical values, constraints, relationships, and the mathematical domain "
            "(e.g., combinatorics, geometry, algebra) relevant to solving the problem. "
            "Provide this information in a structured format."
        )
        extraction = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Explore multiple solution approaches in parallel
        combinatorics_instruction = (
            f"Given the extracted information: {extraction}\n"
            "Solve the problem using combinatorial reasoning. Consider counting principles, "
            "recursive structures, and probabilistic methods if applicable."
        )
        algebra_instruction = (
            f"Given the extracted information: {extraction}\n"
            "Solve the problem using algebraic manipulation. Focus on equations, inequalities, "
            "and functional relationships."
        )
        geometry_instruction = (
            f"Given the extracted information: {extraction}\n"
            "Solve the problem using geometric reasoning. Consider coordinate geometry, "
            "synthetic geometry, and area/volume calculations."
        )

        combinatorics_solution, algebra_solution, geometry_solution = await asyncio.gather(
            self.generate(instruction=combinatorics_instruction, context=self.problem_text),
            self.generate(instruction=algebra_instruction, context=self.problem_text),
            self.generate(instruction=geometry_instruction, context=self.problem_text)
        )

        # Step 3: Refine each solution
        refinement_instruction = (
            "Critique and refine the provided solution. Ensure all constraints are satisfied, "
            "edge cases are considered, and calculations are verified. Provide a detailed explanation."
        )
        refined_combinatorics = await self.revise(instruction=refinement_instruction, context=combinatorics_solution)
        refined_algebra = await self.revise(instruction=refinement_instruction, context=algebra_solution)
        refined_geometry = await self.revise(instruction=refinement_instruction, context=geometry_solution)

        # Step 4: Ensemble decision-making
        ensemble_instruction = (
            "Compare the three refined solutions and select the most robust and mathematically sound one. "
            "Provide a justification for your choice."
        )
        final_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts=[refined_combinatorics, refined_algebra, refined_geometry]
        )

        # Step 5: Summarize the final solution
        summary_instruction = (
            "Condense the final solution into a concise, clear format. Highlight the key steps, "
            "reasoning, and results while preserving mathematical rigor."
        )
        summarized_solution = await self.summarize(instruction=summary_instruction, context=final_solution)

        return summarized_solution