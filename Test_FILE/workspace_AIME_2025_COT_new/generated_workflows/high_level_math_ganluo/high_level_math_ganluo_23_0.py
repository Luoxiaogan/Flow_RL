# Workflow ID: high_level_math_ganluo_23_0
# Benchmark: high_level_math_ganluo
# Data Indices: [5]

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
            "Extract all numerical values, relationships, and constraints from the problem. "
            "Identify the type of mathematical problem (e.g., geometry, algebra, combinatorics) and any specific techniques required. "
            "Organize the information in a structured format."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution strategies
        generate_instruction = (
            f"Using the extracted information: {extracted_info}, propose multiple solution strategies. "
            "Consider different mathematical approaches (e.g., geometric reasoning, algebraic manipulation, casework analysis). "
            "Ensure each strategy addresses all constraints and leads to a complete solution."
        )
        strategies = await asyncio.gather(
            self.generate(instruction=generate_instruction, context=self.problem_text),
            self.generate(instruction=generate_instruction, context=self.problem_text)
        )

        # Step 3: Refine and validate each strategy
        refine_instruction = (
            "Critically evaluate the proposed solution strategy. Check for logical consistency, mathematical correctness, "
            "and adherence to all problem constraints. Identify and address any gaps or errors. Provide a refined version of the solution."
        )
        refined_solutions = await asyncio.gather(
            self.revise(instruction=refine_instruction, context=strategies[0]),
            self.revise(instruction=refine_instruction, context=strategies[1])
        )

        # Step 4: Synthesize the best solution
        ensemble_instruction = (
            "Compare the refined solutions and select the most accurate and efficient one. "
            "Ensure the chosen solution satisfies all problem constraints and provides a clear path to the final answer."
        )
        final_solution = await self.ensemble(instruction=ensemble_instruction, contexts=refined_solutions)

        return final_solution