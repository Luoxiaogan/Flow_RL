# Workflow ID: high_level_math_ganluo_16_0
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
        
        # Step 1: Extract key mathematical components
        extraction_instruction = (
            "Extract all key mathematical components from the problem, including numbers, sets, "
            "divisors, probabilities, and any constraints or conditions. Organize them clearly."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)
        
        # Step 2: Perform mathematical analysis
        analysis_instruction = f"""
        Analyze the extracted components step by step:
        1. Identify all positive integer divisors of any numbers mentioned.
        2. Construct subsets of these divisors as described in the problem.
        3. Calculate probabilities or other required values based on the subset properties.
        Extracted Information: {extracted_info}
        """
        analysis_result = await self.generate(instruction=analysis_instruction, context=self.problem_text)
        
        # Step 3: Explore alternative solution paths in parallel
        combinatorial_instruction = f"""
        Solve the problem using combinatorial reasoning:
        - Count all possible subsets with the given property.
        - Calculate the probability of selecting such subsets.
        Extracted Information: {extracted_info}
        """
        number_theory_instruction = f"""
        Solve the problem using number-theoretic reasoning:
        - Focus on the least common multiple (LCM) condition.
        - Determine which subsets satisfy the LCM property.
        Extracted Information: {extracted_info}
        """
        combinatorial_solution, number_theory_solution = await asyncio.gather(
            self.generate(instruction=combinatorial_instruction, context=self.problem_text),
            self.generate(instruction=number_theory_instruction, context=self.problem_text)
        )
        
        # Step 4: Synthesize results from alternative approaches
        synthesis_instruction = """
        Compare the combinatorial and number-theoretic solutions:
        - Evaluate their correctness and completeness.
        - Select the most robust and accurate solution.
        If both are valid, merge their insights into a single coherent answer.
        """
        final_solution = await self.ensemble(
            instruction=synthesis_instruction,
            contexts=[combinatorial_solution, number_theory_solution]
        )
        
        # Step 5: Refine the final solution
        refinement_instruction = """
        Refine the solution to ensure it satisfies all problem constraints:
        - Verify the probability calculation.
        - Express the result in the required format (e.g., m + n).
        - Check for any errors or omissions.
        """
        refined_solution = await self.revise(instruction=refinement_instruction, context=final_solution)
        
        return refined_solution