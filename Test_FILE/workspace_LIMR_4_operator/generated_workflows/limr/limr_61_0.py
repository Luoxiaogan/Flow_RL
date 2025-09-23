# Workflow ID: limr_61_0
# Benchmark: limr
# Data Indices: [4, 273]

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
        
        # Step 1: Initial Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem to:
            - Identify the mathematical domain (algebra, geometry, etc.)
            - Extract key components (variables, constants, constraints)
            - Classify the problem type (equation, optimization, etc.)
            - Highlight any ambiguities or special cases
            Provide a structured summary.""",
            context=""
        )
        
        # Step 2: Parallel Exploration of Multiple Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis:
                {analysis}
                
                Solve the problem using algebraic methods:
                - Perform symbolic manipulations
                - Solve equations step-by-step
                - Verify intermediate results""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis:
                {analysis}
                
                Solve the problem using geometric reasoning:
                - Visualize shapes and relationships
                - Apply geometric theorems
                - Calculate dimensions and properties""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis:
                {analysis}
                
                Solve the problem using combinatorial techniques:
                - Count possibilities
                - Use permutations and combinations
                - Apply probability principles""",
                context=analysis
            )
        )
        
        # Step 3: Iterative Refinement of Each Approach
        refined_approaches = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this solution:\n{approach}",
                context=approach
            ) for approach in approaches]
        )
        
        # Step 4: Synthesize the Best Solution
        final_solution = await self.ensemble(
            instruction="""Evaluate the refined solutions:
            - Check correctness and completeness
            - Compare elegance and efficiency
            - Select the most appropriate solution
            Provide the final answer in the required format.""",
            contexts_list=refined_approaches
        )
        
        return final_solution