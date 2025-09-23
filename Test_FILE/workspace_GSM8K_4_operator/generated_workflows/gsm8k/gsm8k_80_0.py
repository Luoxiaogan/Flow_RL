# Workflow ID: gsm8k_80_0
# Benchmark: gsm8k
# Data Indices: [220, 210]

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

        # Step 1: Initial Analysis - Extract key information and classify the problem
        analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Classify the problem type (e.g., rate, proportion, distribution, multi-entity). 
            Identify what the question is asking for and any implicit constraints.""",
            context=""
        )

        # Step 2: Dynamic Branching - Adapt workflow based on problem type
        if "rate" in analysis.lower():
            # Rate problem: Focus on relationships between quantities
            solution_steps = await self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Identify the relationship between quantities (e.g., speed = distance / time).
                Propose a step-by-step solution plan.""",
                context=analysis
            )
        elif "proportion" in analysis.lower():
            # Proportion problem: Emphasize scaling and unit conversions
            solution_steps = await self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Identify scaling factors, percentages, or ratios.
                Propose a step-by-step solution plan.""",
                context=analysis
            )
        elif "multi-entity" in analysis.lower():
            # Multi-entity problem: Process each entity in parallel
            entities = await self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Extract all entities and their attributes.
                List them in a structured format.""",
                context=analysis
            )
            entity_solutions = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Solve for entity: {entity} based on the problem context.""",
                    context=entities
                ) for entity in entities.split('\n') if entity.strip()]
            )
            solution_steps = await self.ensemble(
                instruction="Combine solutions for all entities into a unified result.",
                contexts_list=entity_solutions
            )
        else:
            # Default approach for other problem types
            solution_steps = await self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Propose a general step-by-step solution plan.""",
                context=analysis
            )

        # Step 3: Sequential Execution - Solve step-by-step and track intermediate results
        intermediate_results = []
        for step in solution_steps.split('\n'):
            if step.strip():
                result = await self.generate(
                    instruction=f"""Execute this step: {step}
                    Show all calculations and intermediate results.""",
                    context="\n".join(intermediate_results)
                )
                refined_result = await self.revise(
                    instruction=f"""Verify the correctness of this result: {result}
                    Correct any errors and clarify calculations.""",
                    context=result
                )
                intermediate_results.append(refined_result)

        # Step 4: Validation and Refinement - Ensure numerical accuracy
        final_validation = await self.revise(
            instruction=f"""Validate all intermediate results: {intermediate_results}
            Ensure numerical accuracy and logical consistency.
            Propose corrections if necessary.""",
            context="\n".join(intermediate_results)
        )

        # Step 5: Final Synthesis - Extract the numerical answer
        final_answer = await self.generate(
            instruction=f"""Based on the validated results: {final_validation}
            Extract the final numerical answer as a single value.""",
            context=final_validation
        )

        return final_answer.strip()