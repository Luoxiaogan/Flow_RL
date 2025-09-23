# Workflow ID: limr_1_0
# Benchmark: limr
# Data Indices: [98, 164]

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

        # Step 1: Problem Classification and Key Information Extraction
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Geometry (e.g., 3D shapes, coordinate geometry)
            - Number Theory (e.g., modular arithmetic, divisibility)
            - Algebra (e.g., polynomials, equations)
            - Combinatorics (e.g., counting principles, probability)
            - Optimization (e.g., maxima/minima, inequalities)
            
            Extract key entities, numbers, and relationships. Identify constraints and boundary conditions.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Explore solution using geometric techniques: {classification}",
                context=classification
            ),
            self.generate(
                instruction=f"Explore solution using algebraic techniques: {classification}",
                context=classification
            ),
            self.generate(
                instruction=f"Explore solution using combinatorial techniques: {classification}",
                context=classification
            )
        )

        # Step 3: Synthesize Best Approach
        best_approach = await self.ensemble(
            instruction="Select the most promising solution path based on clarity, completeness, and correctness.",
            contexts_list=solution_paths
        )

        # Step 4: Rigorous Validation and Refinement
        validated_solution = await self.revise(
            instruction="Critique and refine the solution. Check for errors, ensure logical consistency, and verify calculations.",
            context=best_approach
        )

        # Step 5: Final Output Formatting
        final_output = await self.summarize(
            instruction="Condense the solution into a precise, formatted answer. Ensure the output is an integer between 000 and 999.",
            context=validated_solution
        )

        return final_output