# Workflow ID: mbpp_74_0
# Benchmark: mbpp
# Data Indices: [177, 141]

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
        import re

        # Step 1: Extract function name and analyze task description
        analysis_task = await self.generate(
            instruction="""Extract the function name from the assert statements and analyze the task description:
            - Identify the function name used in the assert statements.
            - Summarize the task requirements in structured form.
            - Highlight any ambiguities or missing details.""",
            context=""
        )

        # Step 2: Infer problem type and build context
        problem_type_task = await self.generate(
            instruction="""Classify the problem type based on keywords and test cases:
            - Is it related to lists/arrays, mathematics, strings, or other categories?
            - Identify relevant Python modules or functions that might be needed.""",
            context=analysis_task
        )

        # Summarize context for subsequent steps
        context_summary = await self.summarize(
            instruction="Condense the analysis into a concise context for solution generation.",
            context=f"{analysis_task}\n{problem_type_task}"
        )

        # Step 3: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Generate an initial solution based on the following context:
            {context_summary}
            
            Ensure the code includes:
            - Proper function definition with the extracted name.
            - All necessary imports.
            - Handling of edge cases inferred from the test cases.""",
            context=context_summary
        )

        # Step 4: Validate and refine solution
        validation_results = []
        refined_solution = initial_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction="Validate the solution against the test cases and identify any issues.",
                context=refined_solution
            )
            validation_results.append(validation)
            if "error" not in validation.lower():
                break  # Exit loop if no errors
            refined_solution = await self.revise(
                instruction=f"Refine the solution to address the following issues: {validation}",
                context=refined_solution
            )

        # Step 5: Synthesize final solution
        final_solution = await self.ensemble(
            instruction="Select the best solution from the iterations or synthesize a new one.",
            contexts_list=validation_results + [refined_solution]
        )

        # Step 6: Format and return final output
        formatted_output = f"