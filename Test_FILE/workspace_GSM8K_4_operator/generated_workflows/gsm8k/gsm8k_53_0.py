# Workflow ID: gsm8k_53_0
# Benchmark: gsm8k
# Data Indices: [201, 234]

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
            instruction="""Extract all numerical values, entities, relationships, and constraints:
            - Numbers: List all numerical values with their units
            - Entities: Identify people, objects, or places mentioned
            - Relationships: Describe how entities interact (e.g., 'gave,' 'arrived')
            - Constraints: Note any explicit or implicit conditions""",
            context=""
        )

        # Step 2: Refine extraction for completeness
        refined_extraction = await self.revise(
            instruction="Ensure all key components are captured and clarify ambiguities.",
            context=extraction
        )

        # Step 3: Classify problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the refined extraction:
            - Is it a rate problem (distance/speed/time)?
            - Is it a distribution problem (dividing quantities)?
            - Is it a proportion problem (percentages, fractions)?
            - What is the expected answer format?""",
            context=refined_extraction
        )

        # Step 4: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Develop a solution assuming it's a rate problem: {classification}",
                context=refined_extraction
            ),
            self.generate(
                instruction=f"Develop a solution assuming it's a distribution problem: {classification}",
                context=refined_extraction
            ),
            self.generate(
                instruction=f"Develop a solution assuming it's a proportion problem: {classification}",
                context=refined_extraction
            )
        )

        # Step 5: Validate and select the best solution
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Validate this solution for logical consistency and accuracy.",
                context=path
            ) for path in solution_paths]
        )
        best_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=validated_solutions
        )

        # Step 6: Iterative refinement with feedback
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Check for errors or missing steps in the solution.",
                context=best_solution
            )
            if "error" in validation.lower():
                best_solution = await self.revise(
                    instruction=f"Correct the following issues: {validation}",
                    context=best_solution
                )
            else:
                break

        # Step 7: Summarize and extract final answer
        final_answer = await self.summarize(
            instruction="Condense the solution into a single numerical answer with units.",
            context=best_solution
        )

        return final_answer