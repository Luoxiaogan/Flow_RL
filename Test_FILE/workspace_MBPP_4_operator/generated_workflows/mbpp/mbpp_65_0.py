# Workflow ID: mbpp_65_0
# Benchmark: mbpp
# Data Indices: [170]

# --- DO NOT IMPORT HERE ---
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
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Initial Analysis
        analysis_instruction = """Extract the function name from the test cases and understand the task requirements:
        - Identify the function name and its parameters
        - Parse the natural language description to understand the problem
        - Identify potential edge cases from the test examples"""
        initial_analysis = await self.generate(instruction=analysis_instruction, context="")

        # Parallel Exploration
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"Using the analysis: {initial_analysis}\nGenerate a solution using stack-based approach...",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the analysis: {initial_analysis}\nGenerate a solution using recursive approach...",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the analysis: {initial_analysis}\nGenerate a solution using regular expressions...",
                context=initial_analysis
            )
        )

        # Synthesis and Selection
        synthesis_instruction = """Evaluate each solution based on:
        - Correctness: Does it pass all test cases?
        - Efficiency: Is it optimized for performance?
        - Readability: Is the code clean and understandable?"""
        best_solution = await self.ensemble(instruction=synthesis_instruction, contexts_list=solution_attempts)

        # Validation and Iterative Refinement
        validation_instruction = "Validate the solution against the test cases. If it fails, identify the issues."
        validation_result = await self.generate(instruction=validation_instruction, context=best_solution)
        
        refined_solution = best_solution
        iteration_count = 0
        while "error" in validation_result.lower() and iteration_count < 3:
            iteration_count += 1
            refinement_instruction = f"Refine the solution to address the following issues: {validation_result}"
            refined_solution = await self.revise(instruction=refinement_instruction, context=refined_solution)
            
            validation_result = await self.generate(instruction=validation_instruction, context=refined_solution)

        # Final Output
        final_code = refined_solution
        return final_code