# Workflow ID: high_level_math_ganluo_8_0
# Benchmark: high_level_math_ganluo
# Data Indices: [11]

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
            "Extract all equations, inequalities, constraints, and target objectives from the problem. "
            "Identify the mathematical domain (e.g., algebra, geometry, combinatorics) and categorize the components. "
            "Provide a structured breakdown of the problem."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Analyze mathematical structures and formulate strategies
        analysis_instruction = (
            f"Based on the extracted information: {extracted_info}\n"
            "Analyze the mathematical structures involved (e.g., planes, inequalities, regions). "
            "Determine the appropriate techniques to apply (e.g., coordinate geometry, algebraic manipulation, symmetry exploitation). "
            "Formulate a detailed strategy to solve the problem."
        )
        strategy = await self.generate(instruction=analysis_instruction, context=self.problem_text)

        # Step 3: Explore multiple solution approaches in parallel
        approach_1_instruction = (
            f"Using the strategy: {strategy}\n"
            "Solve the problem using algebraic manipulation and direct computation. "
            "Show all steps clearly and verify intermediate results."
        )
        approach_2_instruction = (
            f"Using the strategy: {strategy}\n"
            "Solve the problem using geometric interpretation and visualization. "
            "Describe the geometric structures and their properties. Compute the required quantities."
        )
        results = await asyncio.gather(
            self.generate(instruction=approach_1_instruction, context=self.problem_text),
            self.generate(instruction=approach_2_instruction, context=self.problem_text)
        )

        # Step 4: Synthesize and validate the best solution
        synthesis_instruction = (
            "Compare the following candidate solutions and select the most rigorous and accurate one. "
            "Ensure the chosen solution satisfies all constraints and conditions specified in the problem. "
            "If necessary, synthesize elements from both solutions to form a complete answer."
        )
        best_solution = await self.ensemble(instruction=synthesis_instruction, contexts=results)

        # Step 5: Refine and present the final solution
        refinement_instruction = (
            "Refine the following solution for clarity and correctness. "
            "Ensure the answer is presented in the required format (e.g., $a+b$ if applicable)."
        )
        final_answer = await self.revise(instruction=refinement_instruction, context=best_solution)

        return final_answer