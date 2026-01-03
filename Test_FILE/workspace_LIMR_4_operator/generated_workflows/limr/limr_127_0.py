# Workflow ID: limr_127_0
# Benchmark: limr
# Data Indices: [197, 13]

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
        
        # Phase 1: Initial Analysis and Decomposition
        initial_analysis = await self.generate(
            instruction="""Extract key components, constraints, and relationships from the problem:
            - Identify known quantities and variables
            - List all relationships and equations
            - Highlight any special conditions or boundary cases
            - Suggest potential solution strategies""",
            context=""
        )
        
        structured_summary = await self.summarize(
            instruction="Condense the analysis into a structured summary of key points.",
            context=initial_analysis
        )
        
        # Phase 2: Parallel Solution Exploration
        algebraic_attempt = self.generate(
            instruction=f"""Solve the problem using algebraic methods:
            - Perform symbolic manipulations
            - Solve equations step-by-step
            - Maintain precision in calculations
            
            Problem Summary: {structured_summary}""",
            context=""
        )
        
        geometric_attempt = self.generate(
            instruction=f"""Solve the problem using geometric interpretation:
            - Visualize the problem spatially
            - Apply geometric theorems and properties
            - Use coordinate geometry if applicable
            
            Problem Summary: {structured_summary}""",
            context=""
        )
        
        combinatorial_attempt = self.generate(
            instruction=f"""Solve the problem using combinatorial reasoning:
            - Count possibilities systematically
            - Apply permutations and combinations
            - Use probability principles if needed
            
            Problem Summary: {structured_summary}""",
            context=""
        )
        
        optimization_attempt = self.generate(
            instruction=f"""Solve the problem using optimization techniques:
            - Identify objective functions
            - Apply inequalities and extremal principles
            - Find maxima/minima systematically
            
            Problem Summary: {structured_summary}""",
            context=""
        )
        
        # Execute parallel attempts
        attempts = await asyncio.gather(algebraic_attempt, geometric_attempt, combinatorial_attempt, optimization_attempt)
        
        # Refine each attempt
        refined_attempts = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity, correct errors, and enhance logical flow.",
                context=attempt
            ) for attempt in attempts]
        )
        
        # Phase 3: Ensemble Synthesis
        best_solution = await self.ensemble(
            instruction="""Select the most promising solution or combine insights from multiple attempts:
            - Evaluate logical consistency
            - Assess computational efficiency
            - Ensure alignment with problem constraints
            - Prioritize solutions with clear verification steps""",
            contexts_list=refined_attempts
        )
        
        # Phase 4: Iterative Refinement and Validation
        refined_solution = best_solution
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction="Validate the solution for correctness and completeness.",
                context=refined_solution
            )
            
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Address issues identified in validation: {validation}",
                    context=refined_solution
                )
            else:
                break
        
        # Phase 5: Final Answer Extraction
        final_answer = await self.generate(
            instruction="""Extract the final integer answer:
            - Ensure all calculations are exact
            - Verify the answer satisfies all problem conditions
            - Format the result appropriately""",
            context=refined_solution
        )
        
        return final_answer