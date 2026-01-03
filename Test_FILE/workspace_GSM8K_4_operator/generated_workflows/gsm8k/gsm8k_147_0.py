# Workflow ID: gsm8k_147_0
# Benchmark: gsm8k
# Data Indices: [172, 182]

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

        # Step 1: High-level analysis to classify the problem and extract key components
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify all numerical values and their context
            - Determine the type of problem (e.g., rate, distribution, proportion)
            - Highlight relationships between entities
            - Note any constraints or conditions
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Conditional branching based on problem type
        if "rate" in analysis.lower():
            # Rate problem: Focus on distance, speed, and time
            solution_steps = await self.generate(
                instruction="""Solve the rate problem step-by-step:
                - Identify given values (distance, speed, time)
                - Determine the unknown variable
                - Apply relevant formulas (e.g., distance = speed × time)
                - Show all intermediate calculations""",
                context=analysis
            )
        elif "distribution" in analysis.lower():
            # Distribution problem: Emphasize division and remainders
            solution_steps = await self.generate(
                instruction="""Solve the distribution problem step-by-step:
                - Identify total quantity and number of recipients
                - Perform division to determine shares
                - Handle remainders appropriately
                - Show all intermediate calculations""",
                context=analysis
            )
        else:
            # Default approach for other problem types
            solution_steps = await self.generate(
                instruction="""Solve the problem step-by-step:
                - Identify all numerical values and their roles
                - Determine the sequence of operations
                - Perform calculations in order
                - Show all intermediate results""",
                context=analysis
            )

        # Step 3: Parallel generation of alternative solutions
        alternatives = await asyncio.gather(
            self.revise(
                instruction="Improve clarity and add missing details...",
                context=solution_steps
            ),
            self.revise(
                instruction="Verify calculations and correct errors...",
                context=solution_steps
            )
        )

        # Step 4: Ensemble decision-making to select the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate the alternatives:
            - Check for logical consistency
            - Validate numerical accuracy
            - Ensure clarity and completeness
            Select the most robust solution.""",
            contexts_list=alternatives
        )

        # Step 5: Iterative refinement to ensure correctness
        refined_solution = final_solution
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction="Validate the solution for correctness and completeness...",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Extract the final numerical answer
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer:
            - Ensure it matches the problem's requirements
            - Present only the numerical value (integer or decimal)""",
            context=refined_solution
        )

        return final_answer