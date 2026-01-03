# Workflow ID: limr_16_0
# Benchmark: limr
# Data Indices: [170, 97]

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
        analysis = await self.generate(
            instruction="""Classify the problem into one or more categories:
            - Geometry, Number Theory, Algebra, Combinatorics, Probability, etc.
            Identify key components, constraints, and relationships.
            Provide structured output.""",
            context=""
        )
        
        # Step 2: Parallel Exploration
        strategies = ["algebraic", "geometric", "combinatorial", "numerical"]
        explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"Explore the problem using {strategy} reasoning. "
                            f"Provide detailed steps and intermediate results.",
                context=analysis
            ) for strategy in strategies]
        )
        
        # Step 3: Validation and Refinement
        refined_results = []
        for exploration in explorations:
            validation = await self.generate(
                instruction="Validate the solution. Check for logical consistency, "
                            "mathematical correctness, and adherence to constraints.",
                context=exploration
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction="Refine the solution based on validation feedback. "
                                "Correct errors and fill gaps.",
                    context=exploration
                )
                refined_results.append(refined)
            else:
                refined_results.append(exploration)
        
        # Step 4: Synthesis and Decision
        synthesis = await self.ensemble(
            instruction="Compare and synthesize results from all strategies. "
                        "Select the most complete and accurate solution, "
                        "or combine insights if complementary.",
            contexts_list=refined_results
        )
        
        # Step 5: Final Verification
        final_check = await self.generate(
            instruction="Perform a final verification. Ensure the solution meets "
                        "all problem requirements and is formatted correctly.",
            context=synthesis
        )
        
        return final_check