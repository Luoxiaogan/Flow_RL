# Workflow ID: high_level_math_ganluo_13_0
# Benchmark: high_level_math_ganluo
# Data Indices: [28]

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

        # Step 1: Extract key information and constraints
        extraction_instruction = (
            "Extract all numerical values, geometric relationships, and constraints from the problem. "
            "Identify what the question is asking for and list all relevant details."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches
        algebra_instruction = (
            f"Using the extracted information: {extracted_info}, "
            "solve the problem using algebraic techniques. Focus on equations, variables, and relationships."
        )
        geometry_instruction = (
            f"Using the extracted information: {extracted_info}, "
            "solve the problem using geometric reasoning. Consider shapes, areas, and spatial relationships."
        )
        combinatorics_instruction = (
            f"Using the extracted information: {extracted_info}, "
            "solve the problem using combinatorial methods. Count arrangements or use recursive structures if applicable."
        )
        number_theory_instruction = (
            f"Using the extracted information: {extracted_info}, "
            "solve the problem using number theory. Explore divisibility, modular arithmetic, or prime factorization."
        )

        # Parallel execution of multiple approaches
        results = await asyncio.gather(
            self.generate(instruction=algebra_instruction, context=self.problem_text),
            self.generate(instruction=geometry_instruction, context=self.problem_text),
            self.generate(instruction=combinatorics_instruction, context=self.problem_text),
            self.generate(instruction=number_theory_instruction, context=self.problem_text)
        )

        # Step 3: Refine and critique each solution
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this solution. Ensure it is mathematically sound and satisfies all constraints.",
                context=result
            ) for result in results]
        )

        # Step 4: Ensemble decision-making
        ensemble_instruction = (
            "Compare these solutions and select the most robust and accurate one. "
            "If multiple solutions are valid, synthesize their insights into a single coherent answer."
        )
        final_solution = await self.ensemble(instruction=ensemble_instruction, contexts=refined_results)

        # Step 5: Final verification and simplification
        summary_instruction = (
            "Summarize the final solution in a concise and clear format. "
            "Ensure it satisfies all problem constraints and is expressed in the required form."
        )
        summarized_solution = await self.summarize(instruction=summary_instruction, context=final_solution)

        return summarized_solution