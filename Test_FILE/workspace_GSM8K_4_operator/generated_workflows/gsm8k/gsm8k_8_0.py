# Workflow ID: gsm8k_8_0
# Benchmark: gsm8k
# Data Indices: [254, 148]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract all key entities, numbers, relationships, and constraints:
            - Entities: People, objects, or groups involved.
            - Numbers: All numerical values and their context.
            - Relationships: How entities and numbers are related.
            - Constraints: Any conditions or limitations.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify the problem based on the analysis:
            {analysis}
            
            Categories:
            - Rate problems (distance/speed/time, work rates, etc.)
            - Distribution problems (dividing quantities, sharing, etc.)
            - Proportion problems (percentages, fractions, ratios, etc.)
            - Multi-entity problems (tracking multiple quantities)
            
            Identify the category and suggest a high-level solution strategy.""",
            context=analysis
        )

        # Step 3: Conditional Branching for Solution Strategy
        if "rate" in classification.lower():
            strategy = "Use distance/speed/time relationships or work rate formulas."
        elif "distribution" in classification.lower():
            strategy = "Divide quantities equally or handle remainders as specified."
        elif "proportion" in classification.lower():
            strategy = "Scale values using ratios, percentages, or fractions."
        else:
            strategy = "Track multiple entities and their interactions."

        # Step 4: Sequential Reasoning
        reasoning_steps = []
        current_context = analysis
        for i in range(8):  # Maximum 8 steps
            step = await self.generate(
                instruction=f"""Perform step {i+1} of the solution:
                Current context: {current_context}
                Strategy: {strategy}
                
                - Perform the next logical calculation.
                - Track intermediate results explicitly.
                - Stop if the final answer is reached.""",
                context=current_context
            )
            reasoning_steps.append(step)
            if "final answer" in step.lower():
                break
            current_context += f"\nStep {i+1}: {step}"

        # Step 5: Parallel Validation
        parallel_solutions = await asyncio.gather(
            self.generate(instruction="Solve the problem independently using a different approach.", context=analysis),
            self.generate(instruction="Solve the problem independently using another method.", context=analysis)
        )
        synthesized_solution = await self.ensemble(
            instruction="Compare and synthesize the best solution from the following options.",
            contexts_list=[current_context] + parallel_solutions
        )

        # Step 6: Final Validation
        final_answer = await self.generate(
            instruction=f"""Validate the synthesized solution:
            Synthesized solution: {synthesized_solution}
            
            - Check numerical correctness.
            - Ensure all constraints are satisfied.
            - Present the final answer as a single numerical value.""",
            context=synthesized_solution
        )

        return final_answer