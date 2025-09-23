# Workflow ID: limr_110_0
# Benchmark: limr
# Data Indices: [128, 16]

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
        
        # Step 1: Initial Analysis - Classify problem and extract key information
        initial_analysis = await self.generate(
            instruction="""Classify the problem type (geometry, number theory, etc.) and extract key details:
            - Variables, constants, and relationships
            - Constraints and boundary conditions
            - Expected answer format (integer between 000 and 999)
            Provide a structured summary.""",
            context=""
        )
        
        # Step 2: Strategy Generation - Explore multiple solution approaches
        strategies = await asyncio.gather(
            self.generate(instruction="Develop an algebraic solution approach...", context=initial_analysis),
            self.generate(instruction="Develop a geometric solution approach...", context=initial_analysis),
            self.generate(instruction="Develop a combinatorial solution approach...", context=initial_analysis)
        )
        best_strategy = await self.ensemble(
            instruction="Select the most feasible and clear strategy based on the problem type and constraints.",
            contexts_list=strategies
        )
        
        # Step 3: Sub-Problem Decomposition - Break into smaller parts
        sub_problems = await self.generate(
            instruction=f"Decompose the selected strategy ({best_strategy}) into smaller sub-problems. List them explicitly.",
            context=best_strategy
        )
        sub_problem_solutions = await asyncio.gather(
            *[self.generate(instruction=f"Solve this sub-problem: {sp}", context=sub_problems) for sp in sub_problems.split('\n') if sp.strip()]
        )
        
        # Step 4: Iterative Refinement - Combine and refine solutions
        combined_solution = await self.generate(
            instruction="Combine solutions to sub-problems into a cohesive whole. Ensure logical consistency.",
            context="\n".join(sub_problem_solutions)
        )
        refined_solution = await self.revise(
            instruction="Critique and refine the combined solution. Check calculations, logical flow, and completeness.",
            context=combined_solution
        )
        
        # Step 5: Final Verification - Validate the final answer
        final_verification = await self.revise(
            instruction="Double-check all steps and ensure the final answer meets the required format (integer between 000 and 999).",
            context=refined_solution
        )
        
        return final_verification