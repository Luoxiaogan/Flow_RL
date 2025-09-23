# Workflow ID: limr_114_0
# Benchmark: limr
# Data Indices: [174, 203]

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
        
        # Step 1: Analyze and classify the problem
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Geometry
            - Number Theory
            - Combinatorics
            - Algebra
            - Optimization
            - Sequence and Series
            Provide a detailed breakdown of the problem components and suggest possible solution strategies.""",
            context=""
        )
        
        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop a solution using algebraic manipulation...",
                context=analysis
            ),
            self.generate(
                instruction="Develop a solution using geometric reasoning...",
                context=analysis
            ),
            self.generate(
                instruction="Develop a solution using combinatorial arguments...",
                context=analysis
            )
        )
        
        # Step 3: Verify and refine each solution
        refined_solutions = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Verify the solution and refine any errors or gaps in reasoning...",
                context=strategy
            )
            refined_solutions.append(refined)
        
        # Step 4: Ensemble and synthesize the solutions
        final_solution = await self.ensemble(
            instruction="Synthesize the refined solutions into a final, unified solution. Ensure all steps are logically sound and the answer is an exact integer.",
            contexts_list=refined_solutions
        )
        
        # Step 5: Final verification
        verified_solution = await self.revise(
            instruction="Perform a final verification of the solution. Check against problem constraints and ensure all steps are correct.",
            context=final_solution
        )
        
        return verified_solution