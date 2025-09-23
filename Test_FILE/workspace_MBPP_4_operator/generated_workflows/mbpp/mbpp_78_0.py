# Workflow ID: mbpp_78_0
# Benchmark: mbpp
# Data Indices: [106]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract the function name from the test cases and summarize the task:
            - Identify the function name used in assert statements.
            - Summarize the task description in structured form.
            - List input types, output types, and any constraints or edge cases.""",
            context=""
        )

        # Step 2: Parallel Solution Generation
        drafts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using mathematical reasoning:
                - Translate the task into mathematical operations.
                - Include necessary imports.
                Analysis: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using algorithmic decomposition:
                - Break the task into smaller steps.
                - Include necessary imports.
                Analysis: {analysis}""",
                context=""
            )
        )

        # Step 3: Validation and Feedback
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate the following code against the test cases:
                Code: {draft}
                Provide detailed feedback on any failures.""",
                context=draft
            ) for draft in drafts]
        )

        # Step 4: Iterative Refinement
        max_iterations = 3
        refined_drafts = []
        for i in range(max_iterations):
            refinement_tasks = []
            for draft, validation in zip(drafts, validations):
                if "error" in validation.lower():
                    refinement_tasks.append(
                        self.revise(
                            instruction=f"""Refine the code based on feedback:
                            Feedback: {validation}
                            Original Code: {draft}""",
                            context=draft
                        )
                    )
                else:
                    refined_drafts.append(draft)
            if refinement_tasks:
                drafts = await asyncio.gather(*refinement_tasks)
                validations = await asyncio.gather(
                    *[self.generate(
                        instruction=f"""Validate the following code against the test cases:
                        Code: {draft}
                        Provide detailed feedback on any failures.""",
                        context=draft
                    ) for draft in drafts]
                )
            else:
                break

        # Step 5: Final Synthesis
        final_solution = await self.ensemble(
            instruction="Select the best-performing solution or synthesize elements from multiple drafts.",
            contexts_list=refined_drafts or drafts
        )

        return final_solution