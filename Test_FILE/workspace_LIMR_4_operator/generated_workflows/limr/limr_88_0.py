# Workflow ID: limr_88_0
# Benchmark: limr
# Data Indices: [296, 43]

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

        # Step 1: Initial Analysis - Decompose the problem and classify its type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify key components (variables, constraints, relationships).
            2. Classify the problem type (geometry, number theory, combinatorics, etc.).
            3. List applicable mathematical techniques.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution attempts
        parallel_tasks = [
            self.generate(
                instruction=f"""Solve using {technique}:
                - Show all steps clearly.
                - Maintain full precision.
                - Highlight any assumptions made.""",
                context=initial_analysis
            )
            for technique in ["algebraic manipulation", "combinatorial reasoning", "geometric analysis"]
        ]
        solution_attempts = await asyncio.gather(*parallel_tasks)

        # Step 3: Validation and Refinement - Critique and improve each solution attempt
        refined_solutions = []
        for attempt in solution_attempts:
            validation = await self.generate(
                instruction="Critically evaluate this solution for correctness and completeness.",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix identified issues: {validation}",
                    context=attempt
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(attempt)

        # Step 4: Synthesis and Decision - Select the best solution
        final_answer = await self.ensemble(
            instruction="""Compare all solutions:
            - Evaluate correctness, clarity, and completeness.
            - Resolve any discrepancies.
            - Select the most robust solution.""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Output - Ensure the answer is an integer between 000 and 999
        formatted_answer = await self.generate(
            instruction="""Extract the final answer:
            - Ensure it is an integer between 000 and 999.
            - Format as three digits (e.g., 042).""",
            context=final_answer
        )

        return formatted_answer