# Workflow ID: limr_38_0
# Benchmark: limr
# Data Indices: [232, 78]

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

        # Step 1: Initial Analysis - Classify the problem and extract key components
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Geometry (shapes, volumes, areas, etc.)
            - Number Theory (primes, divisors, modular arithmetic, etc.)
            - Combinatorics (counting, probability, permutations, etc.)
            - Algebra (equations, inequalities, functions, etc.)
            - Optimization (maxima/minima, inequalities, etc.)
            
            Identify key components such as:
            - Variables and constants
            - Relationships and constraints
            - Expected answer format (integer, fraction, etc.)
            
            Provide structured output.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies in Parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a solution using geometric reasoning:
                - Apply relevant formulas
                - Analyze proportions and relationships
                - Ensure precision in calculations""",
                context=classification
            ),
            self.generate(
                instruction=f"""Develop a solution using algebraic manipulation:
                - Solve equations step-by-step
                - Verify intermediate results
                - Maintain full precision""",
                context=classification
            ),
            self.generate(
                instruction=f"""Develop a solution using combinatorial analysis:
                - Count possibilities systematically
                - Apply probability principles
                - Double-check logic""",
                context=classification
            )
        )

        # Step 3: Validate and Refine Each Strategy
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="""Critique and improve this solution:
                - Check for calculation errors
                - Ensure logical consistency
                - Clarify ambiguous steps""",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Synthesize and Select the Best Solution
        final_solution = await self.ensemble(
            instruction="""Evaluate the refined solutions:
            - Select the most accurate and complete solution
            - Resolve any conflicts between alternatives
            - Ensure the final answer is precise and formatted correctly""",
            contexts_list=refined_strategies
        )

        # Step 5: Extract and Format the Final Answer
        final_answer = await self.summarize(
            instruction="""Extract the final answer from the selected solution:
            - Ensure it is an integer between 000 and 999
            - Remove unnecessary details
            - Present in the required format""",
            context=final_solution
        )

        return final_answer