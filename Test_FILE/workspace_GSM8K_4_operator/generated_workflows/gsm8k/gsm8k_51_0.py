# Workflow ID: gsm8k_51_0
# Benchmark: gsm8k
# Data Indices: [28, 46]

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
            instruction="""Extract all relevant information from the problem:
            - Numbers and their units
            - Entities (people, objects, etc.)
            - Relationships and constraints
            - What is being asked for
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify Problem Type
        classification = await self.generate(
            instruction=f"""Classify the problem based on extracted information:
            {extraction}
            
            Categories:
            - Sequential Operations
            - Rate Problems (distance/speed/time, work rates)
            - Distribution (sharing, remainders)
            - Proportions (percentages, fractions, ratios)
            - Multi-entity Tracking
            
            Provide a clear classification and reasoning.""",
            context=extraction
        )

        # Step 3: Plan Solution Strategy
        strategy = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Develop a step-by-step solution strategy:
            - Define intermediate steps
            - Specify arithmetic operations
            - Highlight potential ambiguities or edge cases""",
            context=classification
        )

        # Step 4: Execute Calculations (Iterative Refinement)
        refined_results = []
        for i in range(3):  # Limit iterations to balance thoroughness and efficiency
            calculation = await self.generate(
                instruction=f"""Perform calculations step-by-step:
                Strategy: {strategy}
                
                Show all intermediate results and validate each step.""",
                context=strategy if i == 0 else refined_results[-1]
            )
            validation = await self.revise(
                instruction=f"""Validate the calculations:
                {calculation}
                
                Check for:
                - Arithmetic errors
                - Logical consistency
                - Alignment with problem requirements""",
                context=calculation
            )
            refined_results.append(validation)
            if "error" not in validation.lower():
                break

        # Step 5: Synthesize Final Answer
        final_answer = await self.summarize(
            instruction=f"""Condense the validated results into a single numerical answer:
            Validated Results: {refined_results[-1]}
            
            Ensure the answer is precise and formatted correctly.""",
            context=refined_results[-1]
        )

        return final_answer.strip()