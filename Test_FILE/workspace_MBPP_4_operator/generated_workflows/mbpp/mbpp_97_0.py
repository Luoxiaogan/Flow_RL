# Workflow ID: mbpp_97_0
# Benchmark: mbpp
# Data Indices: [93, 163]

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

        # Step 1: Extract function name and task details
        function_name_analysis = await self.generate(
            instruction="""Extract the function name from the assert statements.
            - Look for patterns like 'assert function_name(args) == expected_output'
            - Identify the function name and its usage context.
            Provide the function name and a brief summary of the task.""",
            context=""
        )

        # Step 2: Parse task description
        task_summary = await self.generate(
            instruction=f"""Analyze the task description:
            Task Description: {self.problem_text}
            Function Name: {function_name_analysis}
            - Identify inputs, outputs, and transformations.
            - List any constraints or edge cases mentioned.""",
            context=function_name_analysis
        )

        # Step 3: Parallel exploration of interpretations
        interpretations = await asyncio.gather(
            self.generate(
                instruction="Interpret the task from a mathematical perspective.",
                context=task_summary
            ),
            self.generate(
                instruction="Interpret the task from a logical/algorithmic perspective.",
                context=task_summary
            ),
            self.generate(
                instruction="Interpret the task from a textual/string manipulation perspective.",
                context=task_summary
            )
        )
        unified_understanding = await self.ensemble(
            instruction="Synthesize these interpretations into a unified understanding of the task.",
            contexts_list=interpretations
        )

        # Step 4: Initial solution attempt
        initial_solution = await self.generate(
            instruction=f"""Generate an initial solution based on the unified understanding:
            Unified Understanding: {unified_understanding}
            - Include all necessary imports.
            - Ensure proper indentation and syntax.
            - Validate against test cases.""",
            context=unified_understanding
        )

        # Step 5: Iterative refinement
        refined_solution = initial_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution against test cases:
                Solution: {refined_solution}
                - Check for correctness and completeness.
                - Identify any errors or missing details.""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution to address the following issues:
                    Issues: {validation}
                    - Correct errors and improve clarity.""",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Final synthesis
        final_code = await self.generate(
            instruction=f"""Ensure the final code is complete and executable:
            Refined Solution: {refined_solution}
            - Include all necessary imports.
            - Maintain proper indentation.
            - Format as a markdown code block.""",
            context=refined_solution
        )

        return final_code