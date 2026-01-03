# Workflow ID: limr_70_0
# Benchmark: limr
# Data Indices: [286, 54]

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

        # Step 1: Initial Analysis and Classification
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Geometry (e.g., 3D geometry, coordinate geometry, trigonometry)
            - Number Theory (e.g., modular arithmetic, divisibility, Diophantine equations)
            - Combinatorics (e.g., counting principles, probability, permutations)
            - Algebra (e.g., polynomial equations, functional equations)
            - Optimization (e.g., maxima/minima, inequalities)
            - Sequence and Series (e.g., recursive sequences, summations)
            
            Identify key components, constraints, and solution requirements. Provide a structured summary.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        sub_problems = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Break the problem into smaller sub-problems. For each sub-problem:
            - Define what needs to be solved
            - Identify applicable methods
            - Specify expected outputs""",
            context=classification
        )

        # Step 3: Parallel Exploration
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the sub-problem:
                {sub_problem}
                
                Use creative approaches and explore multiple methods. Show all steps and reasoning.""",
                context=sub_problems
            ) for sub_problem in sub_problems.split("\n\n") if sub_problem.strip()]
        )

        # Step 4: Iterative Refinement
        refined_solutions = []
        for attempt in solution_attempts:
            for _ in range(3):  # Limit iterations to prevent infinite loops
                validation = await self.generate(
                    instruction=f"""Validate the solution:
                    {attempt}
                    
                    Check for errors, missing steps, or inconsistencies. Provide feedback.""",
                    context=attempt
                )
                if "error" in validation.lower():
                    attempt = await self.revise(
                        instruction=f"""Revise the solution based on feedback:
                        {validation}""",
                        context=attempt
                    )
                else:
                    break
            refined_solutions.append(attempt)

        # Step 5: Synthesis and Final Answer
        synthesis = await self.ensemble(
            instruction="""Synthesize all refined solutions into a unified answer. Ensure:
            - All sub-problems are addressed
            - The final answer is an integer between 000 and 999
            - The reasoning is clear and concise""",
            contexts_list=refined_solutions
        )

        final_answer = await self.summarize(
            instruction="""Condense the synthesis into a concise final answer. Include:
            - The numerical result
            - A brief explanation of the reasoning""",
            context=synthesis
        )

        return final_answer