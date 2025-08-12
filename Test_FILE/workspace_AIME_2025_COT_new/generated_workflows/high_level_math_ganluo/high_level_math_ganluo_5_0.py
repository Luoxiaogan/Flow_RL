# Workflow ID: high_level_math_ganluo_5_0
# Benchmark: high_level_math_ganluo
# Data Indices: [7]

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

        # Step 1: Extract critical components from the problem
        extraction_instruction = (
            "Extract all key mathematical components from the problem, including equations, constraints, "
            "and the goal. Identify any geometric or algebraic structures and specify what needs to be solved."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Perform detailed mathematical analysis
        analysis_instruction = (
            f"Based on the extracted information: {extracted_info}, analyze the problem mathematically. "
            "Interpret any geometric constraints, solve equations step by step, and identify conditions "
            "for the solution to satisfy all constraints. Consider multiple approaches, such as algebraic "
            "manipulation and geometric reasoning."
        )
        analysis = await self.generate(instruction=analysis_instruction, context=self.problem_text)

        # Step 3: Explore multiple solution paths in parallel
        algebraic_instruction = (
            f"Solve the problem using algebraic techniques. Focus on equations and constraints derived from: {analysis}. "
            "Provide a detailed step-by-step solution."
        )
        geometric_instruction = (
            f"Solve the problem using geometric reasoning. Interpret the constraints geometrically based on: {analysis}. "
            "Provide a detailed step-by-step solution."
        )
        algebraic_solution, geometric_solution = await asyncio.gather(
            self.generate(instruction=algebraic_instruction, context=self.problem_text),
            self.generate(instruction=geometric_instruction, context=self.problem_text)
        )

        # Step 4: Evaluate and synthesize solution paths
        ensemble_instruction = (
            "Compare and synthesize the algebraic and geometric solutions. Select the most rigorous and complete "
            "solution that satisfies all constraints. If both are valid, merge their insights."
        )
        final_solution = await self.ensemble(instruction=ensemble_instruction, contexts=[algebraic_solution, geometric_solution])

        # Step 5: Refine and verify the solution
        refinement_instruction = (
            "Critique and refine the selected solution. Ensure it satisfies all constraints, is mathematically "
            "rigorous, and is expressed in the required format. Correct any errors or ambiguities."
        )
        refined_solution = await self.revise(instruction=refinement_instruction, context=final_solution)

        # Step 6: Summarize the final result
        summary_instruction = (
            "Condense the refined solution into a clear, concise answer. Ensure the output adheres to the "
            "required format, such as expressing the sum of all possible values of k as m/n and computing m+n."
        )
        final_answer = await self.summarize(instruction=summary_instruction, context=refined_solution)

        return final_answer