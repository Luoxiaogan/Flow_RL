# Workflow ID: gsm8k_116_0
# Benchmark: gsm8k
# Data Indices: [170, 130]

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

        # Step 1: Initial Analysis - Extract key information and classify the problem
        analysis = await self.generate(
            instruction="""Extract all numerical values, their relationships, and the problem's goal.
            Classify the problem type (e.g., sequential operations, rate problems, distribution, proportions, multi-entity).
            Format the output as:
            - Numbers: [list of values]
            - Relationships: [descriptions of relationships]
            - Goal: [what needs to be solved]
            - Type: [problem classification]""",
            context=""
        )

        # Step 2: Solution Planning - Generate a step-by-step plan
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a detailed step-by-step plan to solve the problem.
            Include:
            - Intermediate calculations
            - Dependencies between steps
            - Final goal""",
            context=analysis
        )

        # Step 3: Parallel Exploration - Generate multiple solution paths
        paths = await asyncio.gather(
            self.generate(instruction=f"Follow this plan strictly: {plan}", context=""),
            self.generate(instruction=f"Explore alternative interpretations: {plan}", context="")
        )

        # Step 4: Iterative Refinement - Validate and refine each path
        refined_paths = []
        for path in paths:
            refined = await self.revise(
                instruction="Check for logical consistency, numerical accuracy, and clarity. Fix any issues.",
                context=path
            )
            refined_paths.append(refined)

        # Step 5: Final Synthesis - Combine validated steps and extract the final answer
        final_solution = await self.ensemble(
            instruction="Select the most consistent and accurate solution. Ensure the final answer is a single numerical value.",
            contexts_list=refined_paths
        )

        # Step 6: Extract Final Answer
        answer = await self.generate(
            instruction="Extract the final numerical answer from the solution. Return only the number.",
            context=final_solution
        )

        return answer.strip()