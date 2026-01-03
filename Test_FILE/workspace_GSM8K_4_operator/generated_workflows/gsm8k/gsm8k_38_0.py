# Workflow ID: gsm8k_38_0
# Benchmark: gsm8k
# Data Indices: [110, 134]

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

        # Step 1: Extract key information (entities, numbers, relationships)
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem.
            Format as a structured list:
            - Entities: [names, roles]
            - Numbers: [values, units, what they represent]
            - Relationships: [how entities and numbers relate]""",
            context=""
        )

        # Step 2: Refine the extraction
        refined_analysis = await self.revise(
            instruction="Validate and refine the extracted information. Ensure completeness and accuracy.",
            context=initial_analysis
        )

        # Step 3: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem based on the refined analysis:
            - Is it sequential operations, rate problems, distribution, proportions, or multi-entity tracking?
            - What calculations are required?""",
            context=refined_analysis
        )

        # Step 4: Conditional branching for solution strategy
        if "sequential" in classification.lower():
            # Sequential operations
            steps = classification.split("\n")
            intermediate_results = []
            for step in steps:
                result = await self.generate(
                    instruction=f"Perform this calculation: {step}",
                    context="\n".join(intermediate_results)
                )
                intermediate_results.append(result)

            final_answer = intermediate_results[-1]

        elif "rate" in classification.lower() or "distribution" in classification.lower():
            # Parallel processing for independent calculations
            calculations = classification.split("\n")
            parallel_results = await asyncio.gather(
                *[self.generate(instruction=f"Compute: {calc}", context=refined_analysis) for calc in calculations]
            )
            final_answer = await self.ensemble(
                instruction="Combine results into a single numerical answer.",
                contexts_list=parallel_results
            )

        else:
            # Default comprehensive approach
            final_answer = await self.generate(
                instruction="Solve the problem using a general mathematical approach.",
                context=refined_analysis
            )

        # Step 5: Validate and refine the final answer
        validated_answer = await self.revise(
            instruction="Ensure the final answer is numerically exact and matches the expected format.",
            context=final_answer
        )

        # Step 6: Extract the final numerical answer
        answer_extraction = await self.summarize(
            instruction="Extract the final numerical answer from the validated solution.",
            context=validated_answer
        )

        return answer_extraction.strip()