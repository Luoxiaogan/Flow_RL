# Workflow ID: drop_72_0
# Benchmark: drop
# Data Indices: [486, 102]

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

        # Step 1: Initial Analysis - Extract entities, classify question type, resolve references
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Classify the question type (arithmetic, counting, comparison, span extraction). 
            Resolve pronouns and partial names to specific entities. 
            Format as a structured list with categories: Entities, Numbers, Relationships, Question Type.""",
            context=""
        )

        # Step 2: Identify Required Operations
        operations = await self.generate(
            instruction=f"""Based on the initial analysis: {initial_analysis}
            Identify the required operations (e.g., addition, subtraction, counting, comparison). 
            Provide a step-by-step plan to solve the problem.""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration - Generate candidate solutions
        operation_tasks = []
        for op in operations.split('\n'):
            if "operation" in op.lower():
                operation_tasks.append(
                    self.generate(
                        instruction=f"""Perform the following operation: {op}. 
                        Ensure all steps are clearly documented and validated against the passage.""",
                        context=initial_analysis
                    )
                )
        candidate_solutions = await asyncio.gather(*operation_tasks)

        # Step 4: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution: {sol}. 
                Check for accuracy, consistency, and adherence to the question requirements.""",
                context=sol
            ) for sol in candidate_solutions]
        )

        # Step 5: Synthesis and Decision
        final_answer = await self.ensemble(
            instruction="""Select the best solution or synthesize multiple perspectives. 
            Ensure the final answer matches the expected format (number, date, or text span).""",
            contexts_list=refined_solutions
        )

        # Step 6: Iterative Refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the final answer: {final_answer}. 
            Identify any inconsistencies or errors.""",
            context=final_answer
        )
        if "error" in validation.lower():
            final_answer = await self.revise(
                instruction=f"""Fix issues: {validation}. 
                Revisit earlier steps to refine the solution.""",
                context=final_answer
            )

        return final_answer