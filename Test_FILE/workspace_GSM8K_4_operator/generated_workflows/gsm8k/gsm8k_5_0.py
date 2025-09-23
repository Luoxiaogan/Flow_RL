# Workflow ID: gsm8k_5_0
# Benchmark: gsm8k
# Data Indices: [125, 274]

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
        
        # Step 1: Entity and Relationship Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 2: Problem Classification
        problem_type = await self.generate(
            instruction=f"""Classify this problem based on extracted entities:
            Entities: {entities}
            
            Categories:
            1. Rate problems (distance/speed/time, work rates, unit prices)
            2. Distribution problems (dividing quantities, equal sharing, remainders)
            3. Proportion problems (percentages, fractions, ratios, scaling)
            4. Sequential operations (step-by-step calculations)
            5. Multi-entity problems (track different quantities for multiple people/objects)
            
            Provide classification and reasoning.""",
            context=entities
        )
        
        # Step 3: Solution Planning
        solution_plan = await self.generate(
            instruction=f"""Create a detailed solution plan based on:
            Entities: {entities}
            Problem Type: {problem_type}
            
            Include:
            - Sequence of operations
            - Intermediate steps
            - Validation checks""",
            context=f"{entities}\n{problem_type}"
        )
        
        # Step 4: Parallel Solution Attempts
        attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using exact calculations:
                Plan: {solution_plan}""",
                context=solution_plan
            ),
            self.generate(
                instruction=f"""Solve using estimation techniques:
                Plan: {solution_plan}""",
                context=solution_plan
            ),
            self.generate(
                instruction=f"""Solve using alternative methods:
                Plan: {solution_plan}""",
                context=solution_plan
            )
        )
        
        # Step 5: Validation and Refinement
        refined_attempts = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine solution attempt",
                context=attempt
            ) for attempt in attempts]
        )
        
        # Step 6: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="Select the best solution based on accuracy, clarity, and adherence to constraints",
            contexts_list=refined_attempts
        )
        
        # Step 7: Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from:
            Solution: {final_solution}
            
            Ensure the answer is in the correct format and numerically exact.""",
            context=final_solution
        )
        
        return final_answer