# Workflow ID: mbpp_55_0
# Benchmark: mbpp
# Data Indices: [162]

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

        # Step 1: Extract function name from assert statements
        function_name_extraction = await self.generate(
            instruction="Extract the function name from the assert statements. "
                        "Return only the function name without parentheses or arguments.",
            context=""
        )
        function_name = function_name_extraction.strip()

        # Step 2: Parse task description to infer requirements
        task_analysis = await self.generate(
            instruction=f"Analyze the task description to infer the computational requirements. "
                        f"Focus on the following:\n"
                        f"- What is the input type?\n"
                        f"- What is the expected output?\n"
                        f"- Are there any constraints or edge cases?\n"
                        f"- What algorithmic approach might be suitable?\n"
                        f"Task Description: {self.problem_text}",
            context=""
        )

        # Step 3: Generate multiple interpretations of the task
        interpretations = await asyncio.gather(
            self.generate(
                instruction="Generate a solution assuming the task involves finding absolute differences.",
                context=task_analysis
            ),
            self.generate(
                instruction="Generate a solution assuming the task involves finding signed differences.",
                context=task_analysis
            ),
            self.generate(
                instruction="Generate a solution assuming the task involves sorting and comparing adjacent elements.",
                context=task_analysis
            )
        )

        # Step 4: Select the best interpretation using ensemble
        best_interpretation = await self.ensemble(
            instruction="Select the interpretation that best matches the test cases. "
                        "Consider consistency with the function name and expected outputs.",
            contexts_list=interpretations
        )

        # Step 5: Generate initial Python code
        initial_code = await self.generate(
            instruction=f"Generate Python code for the function '{function_name}' based on the following interpretation:\n"
                        f"{best_interpretation}\n"
                        f"Ensure the code includes all necessary imports, uses proper indentation, and handles edge cases.",
            context=""
        )

        # Step 6: Validate and refine the code
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the following code against the test cases:\n"
                            f"{initial_code}\n"
                            f"Identify any errors or inconsistencies.",
                context=""
            )
            if "error" in validation.lower():
                initial_code = await self.revise(
                    instruction=f"Fix the following issues in the code:\n"
                                f"{validation}\n"
                                f"Ensure the revised code passes all test cases.",
                    context=initial_code
                )
            else:
                break

        return initial_code