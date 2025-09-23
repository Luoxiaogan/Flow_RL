# Workflow ID: gsm8k_20_0
# Benchmark: gsm8k
# Data Indices: [91, 107]

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

        # Step 1: Initial Analysis - Extract key information
        initial_analysis = await self.generate(
            instruction="""Extract all key entities, numbers, relationships, and constraints from the problem:
            - Identify what is being asked for
            - List all given values and their units
            - Highlight any relationships or formulas mentioned
            - Note any implicit assumptions or conditions""",
            context=""
        )

        # Step 2: Problem Classification - Determine problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {initial_analysis}
            
            Categories:
            - Sequential Operations
            - Rate Problems (distance/speed/time, work rates, etc.)
            - Distribution (dividing quantities, equal sharing, remainders)
            - Proportions (percentages, fractions, ratios, scaling)
            - Multi-entity (tracking different quantities for multiple people/objects)
            
            Provide a clear classification and reasoning.""",
            context=initial_analysis
        )

        # Step 3: Solution Strategy Development - Generate multiple approaches
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a direct computation approach:
                {classification}
                
                Instructions:
                - Use only the given data
                - Perform calculations step-by-step
                - Show intermediate results""",
                context=classification
            ),
            self.generate(
                instruction=f"""Develop a proportional reasoning approach:
                {classification}
                
                Instructions:
                - Identify proportional relationships
                - Use ratios or percentages to solve
                - Validate against given constraints""",
                context=classification
            ),
            self.generate(
                instruction=f"""Develop a unit analysis approach:
                {classification}
                
                Instructions:
                - Track units throughout calculations
                - Ensure dimensional consistency
                - Convert units as needed""",
                context=classification
            )
        )

        # Step 4: Select Best Strategy - Ensemble evaluation
        best_strategy = await self.ensemble(
            instruction="""Evaluate and select the best strategy:
            Criteria:
            - Completeness: Does it address all aspects of the problem?
            - Clarity: Is the reasoning easy to follow?
            - Alignment: Does it match the problem type?
            - Feasibility: Can it be executed step-by-step?""",
            contexts_list=strategies
        )

        # Step 5: Step-by-Step Execution - Iterative loop with validation
        steps = best_strategy.split("\n")
        intermediate_results = []
        for step in steps:
            if not step.strip():
                continue
            result = await self.generate(
                instruction=f"""Execute this step:
                {step}
                
                Instructions:
                - Perform the calculation
                - Show intermediate result
                - Include units if applicable""",
                context="\n".join(intermediate_results)
            )
            validated_result = await self.revise(
                instruction=f"""Validate this result:
                {result}
                
                Instructions:
                - Check for arithmetic errors
                - Ensure consistency with previous steps
                - Flag any issues for correction""",
                context=result
            )
            intermediate_results.append(validated_result)

        # Step 6: Final Answer Synthesis - Combine results into single value
        final_answer = await self.summarize(
            instruction="""Combine all intermediate results into the final answer:
            - Ensure the output is a single numerical value
            - Include units if applicable
            - Round only at the final step if necessary""",
            context="\n".join(intermediate_results)
        )

        return final_answer