# Workflow ID: gsm8k_67_0
# Benchmark: gsm8k
# Data Indices: [39, 200]

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
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, their context, and relationships.
            Classify the problem type (e.g., sequential operations, rate problem, distribution, proportions, multi-entity).
            Identify what the question asks for and any constraints.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}\n"
                            "Solve the problem using direct computation. Show all steps.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}\n"
                            "Solve the problem using estimation techniques. Provide approximate results.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {initial_analysis}\n"
                            "Solve the problem using logical reasoning. Focus on relationships and constraints.",
                context=initial_analysis
            )
        )

        # Step 3: Ensemble Synthesis - Combine insights from multiple paths
        synthesis = await self.ensemble(
            instruction="Synthesize the results from different solution paths into a unified answer. "
                        "Ensure consistency and accuracy.",
            contexts_list=paths
        )

        # Step 4: Validation Loop - Refine and validate the solution
        refined_solution = synthesis
        for _ in range(3):  # Allow up to 3 iterations for refinement
            validation = await self.generate(
                instruction=f"Validate the solution: {refined_solution}\n"
                            "Check for consistency, correctness, and adherence to constraints.",
                context=refined_solution
            )
            if "error" in validation.lower() or "inconsistent" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Refine the solution based on validation feedback: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Output - Condense the solution into a single numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the refined solution. "
                        "Ensure it is exact and formatted correctly.",
            context=refined_solution
        )

        return final_answer