# Workflow ID: limr_63_0
# Benchmark: limr
# Data Indices: [150, 139]

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
        
        # Step 1: Problem Analysis and Decomposition
        problem_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the main components (e.g., variables, equations, constraints).
            - Classify the problem type (e.g., geometry, number theory, combinatorics).
            - Highlight any special cases or edge conditions.
            Provide a structured breakdown.""",
            context=""
        )
        
        # Step 2: Generate Multiple Solution Attempts
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Using the following analysis:
                {problem_analysis}
                
                Solve the problem using an algebraic approach. Show all steps.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Using the following analysis:
                {problem_analysis}
                
                Solve the problem using a geometric approach. Include diagrams if applicable.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Using the following analysis:
                {problem_analysis}
                
                Solve the problem using a combinatorial approach. Focus on counting principles.""",
                context=problem_analysis
            )
        )
        
        # Step 3: Refine Intermediate Results
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Critique and improve this solution. Address any logical gaps or errors.",
                context=solution
            ) for solution in solutions]
        )
        
        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Evaluate the refined solutions:
            - Select the most accurate and complete solution.
            - Ensure the final answer is an integer between 000 and 999.
            - Provide justification for your choice.""",
            contexts_list=refined_solutions
        )
        
        return final_solution