# Workflow ID: high_level_math_ganluo_15_0
# Benchmark: high_level_math_ganluo
# Data Indices: [20]

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

        # Step 1: Decompose the problem into core components
        decomposition_instruction = (
            "Analyze the problem thoroughly. Identify all given values, relationships, constraints, "
            "and what is being asked. Organize this information into clear categories such as "
            "known quantities, unknowns, geometric relationships, algebraic equations, and any "
            "special conditions. Provide a structured breakdown of the problem."
        )
        decomposition = await self.generate(instruction=decomposition_instruction, context=self.problem_text)

        # Step 2: Explore multiple solution paths in parallel
        algebraic_instruction = (
            f"Based on the decomposition: {decomposition}, solve the problem using algebraic methods. "
            "Focus on deriving equations, manipulating expressions, and solving for the unknowns. "
            "Ensure all steps are logically consistent and clearly explained."
        )
        geometric_instruction = (
            f"Based on the decomposition: {decomposition}, solve the problem using geometric reasoning. "
            "Leverage properties of shapes, symmetry, and spatial relationships. Include diagrams "
            "or visual reasoning if necessary."
        )
        combinatorial_instruction = (
            f"Based on the decomposition: {decomposition}, solve the problem using combinatorial or "
            "probabilistic methods. Count arrangements, calculate probabilities, or use recursive "
            "formulas as appropriate."
        )
        paths = await asyncio.gather(
            self.generate(instruction=algebraic_instruction, context=self.problem_text),
            self.generate(instruction=geometric_instruction, context=self.problem_text),
            self.generate(instruction=combinatorial_instruction, context=self.problem_text)
        )

        # Step 3: Refine each solution path
        refine_instruction_template = (
            "Critically analyze the following solution. Check for logical consistency, computational "
            "accuracy, and adherence to the problem's constraints. Improve clarity, eliminate errors, "
            "and ensure the solution is complete. Provide a revised version of the solution."
        )
        refined_paths = await asyncio.gather(
            *[self.revise(instruction=refine_instruction_template, context=path) for path in paths]
        )

        # Step 4: Compare and synthesize solutions
        ensemble_instruction = (
            "Evaluate the following candidate solutions. Select the most elegant, efficient, and "
            "accurate one. If multiple solutions are equally valid, synthesize them into a unified "
            "answer. Justify your choice based on clarity, simplicity, and alignment with the "
            "problem's intent."
        )
        final_solution = await self.ensemble(instruction=ensemble_instruction, contexts=refined_paths)

        # Step 5: Extract the final answer
        summarize_instruction = (
            "Extract the final answer from the provided solution. Ensure it is in the required format, "
            "such as simplified fractions, integers, or boxed results. Provide only the final answer."
        )
        final_answer = await self.summarize(instruction=summarize_instruction, context=final_solution)

        return final_answer