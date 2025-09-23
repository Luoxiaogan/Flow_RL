# Workflow ID: limr_4_0
# Benchmark: limr
# Data Indices: [161, 103]

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
            instruction="""Classify the problem into one of the following categories:
            - Geometry (e.g., shapes, coordinates, transformations)
            - Number Theory (e.g., primes, modular arithmetic, Diophantine equations)
            - Combinatorics (e.g., counting, probability, permutations)
            - Algebra (e.g., polynomials, functional equations, inequalities)
            - Optimization (e.g., maxima/minima, inequalities)
            - Sequence/Series (e.g., recursive sequences, summations)
            
            Extract key components:
            - Variables and constants
            - Constraints and conditions
            - Relationships between elements
            - Expected answer format (e.g., integer between 000 and 999)
            
            Provide a structured summary.""",
            context=""
        )
        
        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop an algebraic solution strategy based on:
                {initial_analysis}
                
                Focus on:
                - Clear variable definitions
                - Logical progression of steps
                - Final answer format""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a combinatorial solution strategy based on:
                {initial_analysis}
                
                Focus on:
                - Counting principles
                - Probability calculations
                - Edge case handling""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a geometric solution strategy based on:
                {initial_analysis}
                
                Focus on:
                - Coordinate systems
                - Transformations
                - Symmetry considerations""",
                context=initial_analysis
            )
        )
        
        # Step 3: Strategy Evaluation and Selection
        selected_strategy = await self.ensemble(
            instruction="""Evaluate the following strategies and select the most appropriate one:
            - Consider simplicity, clarity, and alignment with the problem's requirements
            - Identify any potential pitfalls or ambiguities
            - Choose the strategy that maximizes correctness and efficiency""",
            contexts_list=strategies
        )
        
        # Step 4: Solution Execution
        solution = await self.generate(
            instruction=f"""Implement the selected strategy:
            {selected_strategy}
            
            Ensure:
            - All steps are clearly explained
            - Intermediate results are verified
            - Final answer is presented in the required format""",
            context=selected_strategy
        )
        
        # Step 5: Iterative Refinement
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {solution}
                
                Check for:
                - Logical consistency
                - Arithmetic accuracy
                - Alignment with problem constraints""",
                context=solution
            )
            if "error" in validation.lower():
                solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    {validation}
                    
                    Correct any mistakes and ensure all steps are accurate""",
                    context=solution
                )
            else:
                break
        
        # Step 6: Final Output
        final_output = await self.summarize(
            instruction="""Condense the solution into a concise summary:
            - Highlight key steps and insights
            - Present the final answer in the required format (integer between 000 and 999)""",
            context=solution
        )
        
        return final_output