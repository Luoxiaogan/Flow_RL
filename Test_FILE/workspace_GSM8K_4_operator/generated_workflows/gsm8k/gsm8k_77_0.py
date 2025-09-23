# Workflow ID: gsm8k_77_0
# Benchmark: gsm8k
# Data Indices: [53, 4]

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

        # Step 1: Extract Key Information
        extraction = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem.
            Format as a structured list with categories:
            - Numbers: [values and what they represent]
            - Units: [units associated with numbers]
            - Relationships: [how numbers relate to each other]""",
            context=""
        )

        # Step 2: Classify the Problem
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {extraction}
            
            Determine:
            - Type of problem (e.g., sequential operations, rate, distribution, proportions, multi-entity)
            - Required solution strategy
            - Expected answer format""",
            context=extraction
        )

        # Step 3: Generate Multiple Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using a sequential operations approach:
                {classification}
                
                Show all steps explicitly.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using a rate-based approach:
                {classification}
                
                Focus on distance, speed, time, or work rates.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using a distribution approach:
                {classification}
                
                Handle dividing quantities, equal sharing, or remainders.""",
                context=classification
            )
        )

        # Step 4: Validate and Revise Solutions
        validated_paths = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this solution. Ensure all steps are correct and units are consistent.",
                context=path
            ) for path in paths]
        )

        # Step 5: Ensemble to Select Best Solution
        final_solution = await self.ensemble(
            instruction="Evaluate all solutions and select the most accurate and complete one.",
            contexts_list=validated_paths
        )

        # Step 6: Summarize Final Answer
        summary = await self.summarize(
            instruction="Extract the final numerical answer from the solution. Ensure it is precise and formatted correctly.",
            context=final_solution
        )

        return summary