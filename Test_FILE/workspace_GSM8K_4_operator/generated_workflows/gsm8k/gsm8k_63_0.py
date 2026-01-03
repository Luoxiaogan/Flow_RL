# Workflow ID: gsm8k_63_0
# Benchmark: gsm8k
# Data Indices: [212, 22]

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

        # Step 1: Extract key entities and relationships
        entities_and_relationships = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships:
            - Entities: People, objects, or concepts
            - Numbers: Values and what they represent
            - Relationships: How entities and numbers relate (e.g., 'four times as many', '20 fewer')
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type and identify solution strategies
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {entities_and_relationships}
            
            Categories:
            - Sequential operations (step-by-step calculations)
            - Rate problems (distance/speed/time, work rates, unit prices)
            - Distribution (dividing quantities, equal sharing, remainders)
            - Proportions (percentages, fractions, ratios, scaling)
            - Multi-entity (tracking different quantities for multiple people/objects)
            
            Identify applicable solution strategies and potential pitfalls.""",
            context=entities_and_relationships
        )

        # Step 3: Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a mathematical approach:
                {classification}
                
                Show all steps, including intermediate results and units.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve the problem using a logical reasoning approach:
                {classification}
                
                Focus on relationships and dependencies between entities.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve the problem using a practical estimation approach:
                {classification}
                
                Approximate values and verify reasonableness.""",
                context=classification
            )
        )

        # Step 4: Validate and refine each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Check for calculation errors, logical inconsistencies, or missing details.",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 5: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate, complete, and well-justified solution.",
            contexts_list=refined_solutions
        )

        # Step 6: Extract the final numerical answer
        final_answer = await self.generate(
            instruction="Extract the final numerical answer from the solution. Ensure it is precise and formatted correctly.",
            context=final_solution
        )

        return final_answer