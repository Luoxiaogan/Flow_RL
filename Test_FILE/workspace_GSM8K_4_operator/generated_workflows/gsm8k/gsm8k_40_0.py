# Workflow ID: gsm8k_40_0
# Benchmark: gsm8k
# Data Indices: [296, 166]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships:
            - Identify named entities (people, objects, etc.)
            - List all numbers and their context
            - Describe relationships between entities and numbers
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on extracted information:
            {extraction}
            
            Possible types:
            - Rate problems (distance, speed, time)
            - Distribution problems (dividing quantities)
            - Proportions (percentages, ratios)
            - Multi-entity problems (tracking multiple quantities)
            Provide the type and reasoning.""",
            context=extraction
        )

        # Step 3: Generate initial solution steps
        solution_steps = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Generate a step-by-step solution plan:
            - Define what needs to be calculated
            - Specify the sequence of operations (+, -, ×, ÷)
            - Track intermediate results
            Ensure clarity and logical flow.""",
            context=classification
        )

        # Step 4: Refine and validate solution steps
        refined_steps = await self.revise(
            instruction="""Refine the solution steps:
            - Verify numerical calculations
            - Clarify ambiguous steps
            - Ensure intermediate results are accurate
            - Maintain consistency with the problem statement""",
            context=solution_steps
        )

        # Step 5: Handle alternative interpretations (if needed)
        alternatives = await asyncio.gather(
            self.generate(
                instruction="Explore an alternative interpretation of the problem.",
                context=extraction
            ),
            self.generate(
                instruction="Generate another plausible solution path.",
                context=extraction
            )
        )
        best_solution = await self.ensemble(
            instruction="Select the most plausible solution path based on accuracy and completeness.",
            contexts_list=[refined_steps] + alternatives
        )

        # Step 6: Summarize the final result
        final_result = await self.summarize(
            instruction="Condense the solution into a single numerical answer with brief reasoning.",
            context=best_solution
        )

        return final_result