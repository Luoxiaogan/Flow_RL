# Workflow ID: gsm8k_41_0
# Benchmark: gsm8k
# Data Indices: [292, 119]

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

        # Step 1: Initial Analysis - Extract numbers, units, and relationships
        extraction = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Format the output as a structured list:
            - Numbers: [value1, value2, ...]
            - Units: [unit1, unit2, ...]
            - Relationships: [relationship1, relationship2, ...]""",
            context=""
        )

        # Step 2: Solution Planning - Plan the sequence of operations
        plan = await self.generate(
            instruction=f"""Using the extracted information:
            {extraction}
            
            Plan the sequence of operations needed to solve the problem. 
            Identify the relationships between numbers and determine the order of calculations.""",
            context=extraction
        )

        # Step 3: Parallel Exploration - Generate multiple solution paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a direct approach:
                {plan}""",
                context=plan
            ),
            self.generate(
                instruction=f"""Solve the problem using an alternative approach:
                {plan}""",
                context=plan
            )
        )

        # Step 4: Validation and Refinement - Validate and refine each path
        refined_paths = []
        for path in paths:
            refined = await self.revise(
                instruction="""Validate the solution and refine if necessary:
                - Check for logical consistency
                - Correct calculation errors
                - Add missing details""",
                context=path
            )
            refined_paths.append(refined)

        # Step 5: Synthesis - Select or synthesize the best solution
        final_answer = await self.ensemble(
            instruction="""Evaluate the refined solutions and select the best one:
            - Ensure numerical accuracy
            - Maintain logical consistency
            - Present the final answer as a single numerical value""",
            contexts_list=refined_paths
        )

        return final_answer