# Workflow ID: mbpp_111_0
# Benchmark: mbpp
# Data Indices: [202]

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

        # Step 1: Parallel Fork for Initial Insights
        # Extract function name, analyze task description, and identify edge cases
        function_name_task = self.generate(
            instruction="Extract the function name from the test cases. "
                        "Ensure it matches the format used in the assert statements.",
            context=""
        )
        task_analysis_task = self.generate(
            instruction="Analyze the natural language task description. "
                        "Identify the core logic, required operations, and any implicit constraints.",
            context=""
        )
        edge_cases_task = self.generate(
            instruction="Identify potential edge cases based on the test cases and task description. "
                        "Focus on inputs like empty lists, zero, negative numbers, or large values.",
            context=""
        )
        [function_name, task_analysis, edge_cases] = await asyncio.gather(function_name_task, task_analysis_task, edge_cases_task)

        # Step 2: Hierarchical Decomposition
        # Combine insights into a structured plan
        structured_plan = await self.generate(
            instruction=f"Combine the following insights into a structured plan:\n"
                        f"Function Name: {function_name}\n"
                        f"Task Analysis: {task_analysis}\n"
                        f"Edge Cases: {edge_cases}\n"
                        f"Define the function signature, core logic, and how to handle edge cases.",
            context=f"{function_name}\n{task_analysis}\n{edge_cases}"
        )

        # Step 3: Code Generation
        initial_code = await self.generate(
            instruction=f"Generate Python code based on the structured plan:\n{structured_plan}\n"
                        f"Include necessary imports, proper indentation, and complete function definition.",
            context=structured_plan
        )

        # Step 4: Validation and Refinement Loop
        max_iterations = 5
        for iteration in range(max_iterations):
            validation = await self.generate(
                instruction=f"Validate the generated code against the test cases:\n{initial_code}\n"
                            f"Identify any errors, missing logic, or edge case handling issues.",
                context=initial_code
            )
            if "error" not in validation.lower() and "fail" not in validation.lower():
                break  # Exit loop if validation passes
            initial_code = await self.revise(
                instruction=f"Refine the code based on validation feedback:\n{validation}",
                context=initial_code
            )

        # Step 5: Conditional Branching for Alternative Strategies
        if "error" in validation.lower() or "fail" in validation.lower():
            alternative_strategies = await asyncio.gather(
                self.generate(
                    instruction="Solve the problem using a mathematical approach. "
                                "Focus on formulas and direct computations.",
                    context=structured_plan
                ),
                self.generate(
                    instruction="Solve the problem using an iterative algorithm. "
                                "Focus on loops and step-by-step processing.",
                    context=structured_plan
                )
            )
            refined_code = await self.ensemble(
                instruction="Select the best solution from the alternative strategies. "
                            "Prioritize correctness, simplicity, and adherence to test cases.",
                contexts_list=alternative_strategies
            )
            return refined_code

        return initial_code