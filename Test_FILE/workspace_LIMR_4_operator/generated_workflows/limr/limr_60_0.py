# Workflow ID: limr_60_0
# Benchmark: limr
# Data Indices: [0, 61]

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
        
        # Step 1: Problem Classification
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            - Algebraic (polynomials, equations, inequalities)
            - Geometric (shapes, coordinates, transformations)
            - Combinatorial (counting, permutations, probability)
            - Number Theory (divisibility, primes, modular arithmetic)
            - Optimization (maxima/minima, inequalities)
            Provide a clear rationale for your classification.""",
            context=""
        )
        
        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(instruction="Develop an algebraic solution strategy.", context=classification),
            self.generate(instruction="Develop a geometric solution strategy.", context=classification),
            self.generate(instruction="Develop a combinatorial solution strategy.", context=classification),
            self.generate(instruction="Develop a number theory-based solution strategy.", context=classification),
            self.generate(instruction="Develop an optimization-based solution strategy.", context=classification)
        )
        
        # Step 3: Select Best Strategy
        best_strategy = await self.ensemble(
            instruction="Evaluate the feasibility, rigor, and efficiency of each strategy. Select the most promising one.",
            contexts_list=strategies
        )
        
        # Step 4: Execute Strategy Step-by-Step
        solution_steps = []
        current_context = best_strategy
        for i in range(5):  # Limit to 5 steps for practicality
            step_solution = await self.generate(
                instruction=f"Execute step {i+1} of the solution. Ensure logical progression and maintain precision.",
                context=current_context
            )
            validation = await self.revise(
                instruction="Validate this step. Identify and correct any errors.",
                context=step_solution
            )
            solution_steps.append(validation)
            current_context = validation
        
        # Step 5: Synthesize Final Answer
        final_answer = await self.summarize(
            instruction="Condense the solution into a concise final answer. Ensure clarity and precision.",
            context="\n".join(solution_steps)
        )
        
        return final_answer