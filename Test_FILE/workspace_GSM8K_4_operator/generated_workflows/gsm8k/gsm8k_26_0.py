# Workflow ID: gsm8k_26_0
# Benchmark: gsm8k
# Data Indices: [281, 244]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract key entities, numbers, and relationships:
            - Who or what is involved?
            - What actions or events occur?
            - What numerical values are provided?
            - What is the question asking for?""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify the problem based on the analysis:
            {initial_analysis}
            
            Categories:
            - Sequential Operations
            - Rate Problems (distance/speed/time, work rates)
            - Distribution (dividing quantities, sharing)
            - Proportions (percentages, fractions, ratios)
            - Multi-entity (tracking multiple people/objects)
            
            Provide a clear classification and justification.""",
            context=initial_analysis
        )

        # Step 3: Dynamic Strategy Selection
        if "sequential" in classification.lower():
            solution_path = "sequential"
        elif "rate" in classification.lower():
            solution_path = "rate"
        elif "distribution" in classification.lower():
            solution_path = "distribution"
        elif "proportions" in classification.lower():
            solution_path = "proportions"
        else:
            solution_path = "general"

        # Step 4: Parallel Exploration for Ambiguity
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Solve assuming current context:
                {initial_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve assuming alternative context:
                {initial_analysis}""",
                context=""
            )
        )

        # Step 5: Ensemble Synthesis
        synthesized_solution = await self.ensemble(
            instruction="Select the most plausible solution based on consistency and completeness.",
            contexts_list=interpretations
        )

        # Step 6: Iterative Refinement
        refined_solution = synthesized_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                
                Check for:
                - Logical consistency
                - Correct calculations
                - Alignment with problem requirements""",
                context=""
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Step 7: Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from the solution:
            {refined_solution}
            
            Ensure the answer is:
            - Numerically exact
            - In the required format (integer or decimal)""",
            context=""
        )

        return final_answer