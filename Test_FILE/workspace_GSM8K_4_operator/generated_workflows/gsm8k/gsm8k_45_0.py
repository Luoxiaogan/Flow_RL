# Workflow ID: gsm8k_45_0
# Benchmark: gsm8k
# Data Indices: [8, 259]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Phase 1: Information Extraction
        extracted_info = await self.generate(
            instruction="""Extract all relevant information from the problem:
            - Numerical values and their units
            - Relationships between entities
            - Key constraints or conditions
            Format as a structured list.""",
            context=""
        )

        # Phase 2: Solution Planning
        solution_plan = await self.generate(
            instruction=f"""Using the extracted information:
            {extracted_info}
            
            Create a step-by-step plan to solve the problem:
            - Identify required calculations
            - Specify order of operations
            - Note any unit conversions needed
            - Highlight potential pitfalls or ambiguities""",
            context=extracted_info
        )

        # Phase 3: Parallel Exploration (if applicable)
        # Check if multiple solution paths exist
        needs_parallel = "multiple" in solution_plan.lower() or "alternative" in solution_plan.lower()
        if needs_parallel:
            parallel_paths = await asyncio.gather(
                self.generate(
                    instruction="Solve using method A...",
                    context=solution_plan
                ),
                self.generate(
                    instruction="Solve using method B...",
                    context=solution_plan
                )
            )
            best_path = await self.ensemble(
                instruction="Select the most accurate and efficient solution path.",
                contexts_list=parallel_paths
            )
        else:
            best_path = solution_plan

        # Phase 4: Iterative Refinement
        refined_result = best_path
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the current solution for correctness and completeness.",
                context=refined_result
            )
            if "error" in validation.lower():
                refined_result = await self.revise(
                    instruction=f"Fix issues identified during validation: {validation}",
                    context=refined_result
                )
            else:
                break

        # Phase 5: Final Synthesis
        final_answer = await self.generate(
            instruction=f"""Based on the refined solution:
            {refined_result}
            
            Extract the final numerical answer in the required format.
            Ensure the result is exact and properly formatted.""",
            context=refined_result
        )

        return final_answer