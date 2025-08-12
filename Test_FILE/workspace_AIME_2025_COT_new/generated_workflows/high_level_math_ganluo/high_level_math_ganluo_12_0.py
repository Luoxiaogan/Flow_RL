# Workflow ID: high_level_math_ganluo_12_0
# Benchmark: high_level_math_ganluo
# Data Indices: [4]

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

        # Step 1: Extract key information from the problem
        extract_instruction = (
            "Extract all numerical values, constraints, and conditions from the problem. "
            "Identify the type of mathematical problem (e.g., combinatorics, number theory, geometry). "
            "Highlight any patterns, symmetries, or special cases that might simplify the solution."
        )
        extracted_info = await self.generate(instruction=extract_instruction, context=self.problem_text)

        # Step 2: Explore multiple solution paths in parallel
        algebraic_instruction = (
            f"Using the extracted information: {extracted_info}, solve the problem using algebraic methods. "
            "Focus on equations, inequalities, and functional relationships. Provide step-by-step reasoning."
        )
        combinatorial_instruction = (
            f"Using the extracted information: {extracted_info}, solve the problem using combinatorial methods. "
            "Consider counting techniques, recursive formulas, and generating functions. Provide step-by-step reasoning."
        )
        geometric_instruction = (
            f"Using the extracted information: {extracted_info}, solve the problem using geometric methods. "
            "Apply coordinate geometry, synthetic geometry, or trigonometric principles. Provide step-by-step reasoning."
        )

        results = await asyncio.gather(
            self.generate(instruction=algebraic_instruction, context=self.problem_text),
            self.generate(instruction=combinatorial_instruction, context=self.problem_text),
            self.generate(instruction=geometric_instruction, context=self.problem_text)
        )

        # Step 3: Evaluate and select the best solution
        ensemble_instruction = (
            "Compare the following candidate solutions and select the most accurate, complete, and elegant one. "
            "If possible, synthesize elements from multiple solutions to create an improved version. "
            "Ensure the final solution satisfies all problem constraints and is mathematically sound."
        )
        best_solution = await self.ensemble(instruction=ensemble_instruction, contexts=results)

        # Step 4: Verify and refine the solution
        verify_instruction = (
            "Critically analyze the provided solution. Check whether it satisfies all constraints and conditions. "
            "Address any ambiguities or missing steps. Ensure the solution is clear, concise, and correct."
        )
        refined_solution = await self.revise(instruction=verify_instruction, context=best_solution)

        # Step 5: Summarize the final solution
        summary_instruction = (
            "Summarize the solution in a concise yet complete manner. Include all key steps, reasoning, and the final answer. "
            "Format the summary for clarity and readability."
        )
        final_summary = await self.summarize(instruction=summary_instruction, context=refined_solution)

        return final_summary