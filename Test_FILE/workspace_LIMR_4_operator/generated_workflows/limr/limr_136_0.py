# Workflow ID: limr_136_0
# Benchmark: limr
# Data Indices: [107, 147]

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
        
        # Initial Analysis: Classify problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Classify this problem into subdomains (geometry, number theory, algebra, etc.).
            Identify key components, variables, and constraints.
            Format as structured list with categories:
            - Subdomain: [classification]
            - Variables: [list of variables]
            - Constraints: [list of constraints]
            - Expected Answer Format: [description]""",
            context=""
        )
        
        # Parallel Exploration: Generate multiple solution attempts
        parallel_solutions = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic methods. Show all steps and maintain precision.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using geometric methods. Include diagrams if applicable.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using combinatorial or probabilistic methods. Enumerate all cases.",
                context=initial_analysis
            )
        )
        
        # Iterative Refinement: Critique and improve solutions
        refined_solutions = []
        for solution in parallel_solutions:
            refined = await self.revise(
                instruction="Critique this solution. Check for logical gaps, calculation errors, and missing details. Improve clarity and rigor.",
                context=solution
            )
            refined_solutions.append(refined)
        
        # Synthesis and Decision-Making: Select the best solution
        final_solution = await self.ensemble(
            instruction="Evaluate all solutions. Select the most complete, accurate, and well-reasoned approach. Resolve conflicts if necessary.",
            contexts_list=refined_solutions
        )
        
        # Final Verification: Ensure the solution meets all constraints
        verified_solution = await self.revise(
            instruction="Verify the final solution. Ensure all constraints are satisfied, calculations are correct, and the answer is in the required format.",
            context=final_solution
        )
        
        return verified_solution