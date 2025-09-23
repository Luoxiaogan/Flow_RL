# Workflow ID: gsm8k_12_0
# Benchmark: gsm8k
# Data Indices: [297, 10]

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

        # Initial analysis to extract key components
        initial_analysis = await self.generate(
            instruction="""Extract all key components from the problem:
            - Numbers and their context
            - Entities involved (people, objects, etc.)
            - Relationships and operations mentioned
            - What is being asked for
            Present this information in a structured format.""",
            context=""
        )

        # Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the analysis:
            {initial_analysis}
            
            Categories:
            1. Sequential Operations
            2. Rate Problems
            3. Distribution
            4. Proportions
            5. Multi-entity Tracking
            
            Provide a clear classification and reasoning.""",
            context=initial_analysis
        )

        # Conditional branching based on classification
        if "Sequential Operations" in classification:
            solution = await self.sequential_operations(initial_analysis)
        elif "Rate Problems" in classification:
            solution = await self.rate_problems(initial_analysis)
        elif "Distribution" in classification:
            solution = await self.distribution(initial_analysis)
        elif "Proportions" in classification:
            solution = await self.proportions(initial_analysis)
        elif "Multi-entity Tracking" in classification:
            solution = await self.multi_entity_tracking(initial_analysis)
        else:
            # Default comprehensive approach
            solution = await self.comprehensive_approach(initial_analysis)

        # Final refinement and validation
        refined_solution = await self.revise(
            instruction="Refine the solution for clarity and correctness. Validate all calculations.",
            context=solution
        )

        # Summarize the final answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the refined solution.",
            context=refined_solution
        )

        return final_answer

    async def sequential_operations(self, context):
        steps = await self.generate(
            instruction=f"""Break down the problem into sequential steps:
            {context}
            
            Each step should include:
            - Operation to perform
            - Numbers involved
            - Intermediate result""",
            context=context
        )
        return steps

    async def rate_problems(self, context):
        rates = await self.generate(
            instruction=f"""Identify and calculate rates involved:
            {context}
            
            Include:
            - Ratios and proportions
            - Units and conversions
            - Final calculation""",
            context=context
        )
        return rates

    async def distribution(self, context):
        distribution = await self.generate(
            instruction=f"""Distribute quantities as described:
            {context}
            
            Include:
            - Division and sharing
            - Handling remainders
            - Final distribution""",
            context=context
        )
        return distribution

    async def proportions(self, context):
        proportions = await self.generate(
            instruction=f"""Calculate proportions and percentages:
            {context}
            
            Include:
            - Fractional parts
            - Scaling factors
            - Final proportion""",
            context=context
        )
        return proportions

    async def multi_entity_tracking(self, context):
        entities = await self.generate(
            instruction=f"""Track quantities for multiple entities:
            {context}
            
            Include:
            - Separate calculations for each entity
            - Combined results
            - Final tally""",
            context=context
        )
        return entities

    async def comprehensive_approach(self, context):
        comprehensive = await self.generate(
            instruction=f"""Apply a general problem-solving framework:
            {context}
            
            Include:
            - All relevant calculations
            - Logical reasoning
            - Final solution""",
            context=context
        )
        return comprehensive