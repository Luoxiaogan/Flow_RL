# Workflow ID: limr_42_0
# Benchmark: limr
# Data Indices: [253, 246]

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
            instruction="""Analyze the problem structure:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key components, constraints, and relationships
            - Highlight any special conditions or edge cases
            Provide a structured breakdown.""",
            context=""
        )
        
        # Step 2: Parallel Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop an algebraic solution:
                - Use equations, inequalities, and transformations
                - Show all steps clearly
                - Validate intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a geometric solution:
                - Use diagrams, coordinates, and trigonometric identities
                - Highlight spatial relationships
                - Verify geometric properties""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a combinatorial solution:
                - Apply counting principles, permutations, and combinations
                - Consider probabilistic reasoning if applicable
                - Ensure logical consistency""",
                context=initial_analysis
            )
        )
        
        # Step 3: Intermediate Validation
        validated_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this strategy:
                - Check for logical consistency
                - Ensure precision and correctness
                - Flag any errors or gaps""",
                context=strategy
            ) for strategy in strategies]
        )
        
        # Step 4: Synthesis and Selection
        synthesis = await self.ensemble(
            instruction="""Compare and synthesize strategies:
            - Evaluate completeness, elegance, and feasibility
            - Select the most promising approach
            - Merge complementary insights if necessary""",
            contexts_list=validated_strategies
        )
        
        # Step 5: Iterative Refinement
        refined_solution = synthesis
        for _ in range(3):  # Allow up to 3 refinement iterations
            refinement = await self.revise(
                instruction=f"""Refine the solution:
                - Address flagged issues
                - Improve clarity and rigor
                - Validate against constraints""",
                context=refined_solution
            )
            if "error" not in refinement.lower():
                break
            refined_solution = refinement
        
        # Step 6: Final Output
        final_output = await self.summarize(
            instruction="""Summarize the solution:
            - Highlight key insights
            - Present the final answer in the required format
            - Ensure brevity and clarity""",
            context=refined_solution
        )
        
        return final_output