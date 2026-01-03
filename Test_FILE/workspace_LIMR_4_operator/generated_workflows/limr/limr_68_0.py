# Workflow ID: limr_68_0
# Benchmark: limr
# Data Indices: [252, 211]

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
        
        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Extract key components of the problem:
            - Variables and constants
            - Constraints and relationships
            - Knowns and unknowns
            - Problem type (geometry, number theory, etc.)
            Present in a structured format.""",
            context=""
        )
        
        # Step 2: Identify Solution Approaches
        approaches = await self.generate(
            instruction=f"""Based on the decomposition:
            {decomposition}
            
            Identify multiple solution approaches:
            - Algebraic methods
            - Geometric interpretations
            - Combinatorial techniques
            - Number-theoretic tools
            List all viable strategies.""",
            context=decomposition
        )
        
        # Step 3: Explore Parallel Paths
        parallel_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"Develop solution using approach: {approach}",
                context=decomposition
            ) for approach in approaches.split('\n') if approach.strip()]
        )
        
        # Step 4: Validate and Refine Solutions
        refined_paths = []
        for path in parallel_paths:
            validation = await self.generate(
                instruction=f"Validate the solution: {path}",
                context=decomposition
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=path
                )
                refined_paths.append(refined)
            else:
                refined_paths.append(path)
        
        # Step 5: Synthesize Best Solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=refined_paths
        )
        
        # Step 6: Final Verification
        verified_solution = await self.revise(
            instruction="Ensure the solution is precise and adheres to problem constraints.",
            context=final_solution
        )
        
        return verified_solution