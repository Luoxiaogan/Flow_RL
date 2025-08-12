# Workflow ID: high_level_math_ganluo_3_0
# Benchmark: high_level_math_ganluo
# Data Indices: [21]

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

        # Step 1: Extract key components and structure the problem
        extraction_instruction = (
            "Extract all key components from the problem, including numerical values, "
            "constraints, and relationships. Identify the mathematical domain (e.g., number theory, combinatorics)."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Perform detailed mathematical analysis
        analysis_instruction = (
            f"Based on the extracted information: {extracted_info}, analyze the problem mathematically. "
            "Identify patterns, apply domain-specific techniques, and outline intermediate steps."
        )
        analysis = await self.generate(instruction=analysis_instruction, context=self.problem_text)

        # Step 3: Explore multiple solution paths in parallel
        approach_1_instruction = (
            f"Using the analysis: {analysis}, solve the problem using combinatorial reasoning. "
            "Focus on subset properties and probabilities."
        )
        approach_2_instruction = (
            f"Using the analysis: {analysis}, solve the problem using number-theoretic reasoning. "
            "Focus on divisor properties and least common multiples."
        )
        results = await asyncio.gather(
            self.generate(instruction=approach_1_instruction, context=self.problem_text),
            self.generate(instruction=approach_2_instruction, context=self.problem_text)
        )

        # Step 4: Evaluate and synthesize the best solution
        synthesis_instruction = (
            "Compare the following approaches and select the most rigorous and complete solution. "
            "Ensure the chosen solution satisfies all problem constraints."
        )
        best_solution = await self.ensemble(instruction=synthesis_instruction, contexts=results)

        # Step 5: Refine the final solution
        refinement_instruction = (
            "Critique and refine the following solution. Ensure clarity, correctness, and proper formatting. "
            "Box the final answer if applicable."
        )
        refined_solution = await self.revise(instruction=refinement_instruction, context=best_solution)

        return refined_solution