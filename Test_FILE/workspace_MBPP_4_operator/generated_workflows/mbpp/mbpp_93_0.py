# Workflow ID: mbpp_93_0
# Benchmark: mbpp
# Data Indices: [197, 131]

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
        
        # Phase 1: Initial Analysis and Function Extraction
        initial_analysis = await self.generate(
            instruction="Carefully analyze the test cases to identify the exact function name. "
                        "Then, parse the natural language description to understand the task fully. "
                        "Highlight any ambiguities or unclear requirements.",
            context=""
        )
        
        # Phase 2: Parallel Solution Exploration
        mathematical_solution, iterative_solution, stdlib_solution = await asyncio.gather(
            self.generate(
                instruction="Formulate a mathematical solution using equations and precise calculations.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop an iterative approach using loops and conditionals.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Utilize Python’s standard library functions to achieve the task efficiently.",
                context=initial_analysis
            )
        )
        
        # Phase 3: Ensemble Selection and Refinement
        selected_solution = await self.ensemble(
            instruction="Compare the proposed solutions based on clarity, efficiency, and alignment with Pythonic conventions. "
                        "Choose the most robust and maintainable approach.",
            contexts_list=[mathematical_solution, iterative_solution, stdlib_solution]
        )
        
        # Phase 4: Code Generation and Validation
        final_code = await self.generate(
            instruction="Write complete Python code that includes all required imports, follows 4-space indentation, "
                        "and matches the function name from the test cases. Ensure the code handles typical edge cases "
                        "and passes all assertions.",
            context=selected_solution
        )
        
        # Phase 5: Conditional Revision (if needed)
        validation_result = await self.generate(
            instruction="Validate the generated code against the provided test cases. "
                        "Identify any discrepancies or errors.",
            context=final_code
        )
        
        if "error" in validation_result.lower():
            revised_code = await self.revise(
                instruction="Identify and fix any errors or inefficiencies in the generated code. "
                            "Enhance clarity and ensure compliance with Python best practices.",
                context=final_code
            )
            final_code = revised_code
        
        return final_code