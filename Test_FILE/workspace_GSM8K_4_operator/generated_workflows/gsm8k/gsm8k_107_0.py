# Workflow ID: gsm8k_107_0
# Benchmark: gsm8k
# Data Indices: [175, 38]

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

        # Step 1: Analyze the problem structure
        analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Classify the problem type (e.g., sequential operations, rate problems). Identify what the question is asking for. 
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Generate a detailed solution plan
        plan = await self.generate(
            instruction=f"""Based on the analysis: {analysis}
            Create a step-by-step plan to solve the problem. Include:
            - Sequence of calculations
            - Intermediate goals
            - Constraints and conditions""",
            context=analysis
        )

        # Step 3: Execute sub-problems in parallel
        sub_problems = await self.generate(
            instruction=f"""Break the plan into independent sub-problems. 
            Generate instructions for solving each sub-problem separately.""",
            context=plan
        )
        sub_problem_tasks = [
            self.generate(instruction=sub_problem, context="")
            for sub_problem in sub_problems.split("\n") if sub_problem.strip()
        ]
        sub_results = await asyncio.gather(*sub_problem_tasks)

        # Step 4: Validate and refine intermediate results
        validated_results = []
        for result in sub_results:
            validation = await self.revise(
                instruction="Check for arithmetic accuracy, logical consistency, and adherence to constraints.",
                context=result
            )
            validated_results.append(validation)

        # Step 5: Synthesize final answer
        synthesis = await self.ensemble(
            instruction="Combine all validated results into a single numerical answer. Ensure clarity and precision.",
            contexts_list=validated_results
        )
        final_answer = await self.summarize(
            instruction="Extract the final numerical value from the synthesis.",
            context=synthesis
        )

        return final_answer