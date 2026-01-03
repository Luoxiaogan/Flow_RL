# Workflow ID: mbpp_4_0
# Benchmark: mbpp
# Data Indices: [344]

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

        # Step 1: Initial Analysis - Extract function name and parse task description
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and summarize the task requirements:
            - Function name must match the one in the assert statements
            - Identify input types and expected output format
            - Highlight any constraints or special conditions""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution attempts
        attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Implement the function directly based on the task description:
                - Use basic Python constructs
                - Ensure proper indentation and syntax
                - Include necessary imports at the top""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Leverage Python's standard library to implement the function:
                - Identify relevant modules (e.g., math, itertools)
                - Use built-in functions where applicable
                - Keep the implementation concise and efficient""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Handle edge cases explicitly:
                - Consider empty inputs, invalid types, and boundary conditions
                - Add error handling where necessary
                - Ensure the function is robust""",
                context=analysis
            )
        )

        # Step 3: Synthesis and Selection - Choose the best solution
        synthesis = await self.ensemble(
            instruction="Select the most complete and accurate solution or merge complementary approaches",
            contexts_list=attempts
        )

        # Step 4: Refinement Loop - Iteratively improve the solution
        refined_solution = synthesis
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction="Validate the solution against the test cases and identify issues",
                context=refined_solution
            )
            if "error" in validation.lower() or "missing" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Fix identified issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Final Output
        return refined_solution