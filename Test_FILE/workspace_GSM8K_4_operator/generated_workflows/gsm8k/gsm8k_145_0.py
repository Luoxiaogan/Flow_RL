# Workflow ID: gsm8k_145_0
# Benchmark: gsm8k
# Data Indices: [188, 113]

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

        # Step 1: Extract key information and plan the solution
        extraction = await self.generate(
            instruction="""Extract all numerical values, their contexts, and relationships:
            - Identify what each number represents (e.g., quantity, rate, percentage).
            - Highlight relationships between numbers (e.g., 'twice as many', 'total').
            - Note any implicit constraints or conditions.
            Format as a structured list.""",
            context=""
        )

        # Step 2: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information:
                {extraction}
                
                Solve the problem step-by-step, showing all calculations.
                Focus on direct computation.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {extraction}
                
                Solve the problem step-by-step, focusing on proportional reasoning.""",
                context=extraction
            )
        )

        # Step 3: Validate and refine each solution path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Check calculations for errors and improve clarity.",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Summarize each refined path
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Condense the solution into key steps and final answer.",
                context=path
            ) for path in refined_paths]
        )

        # Step 5: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=summaries
        )

        # Step 6: Extract and return the final numerical answer
        answer = await self.generate(
            instruction=f"""From the final solution:
            {final_solution}
            
            Extract the numerical answer only, ensuring it's exact.""",
            context=final_solution
        )

        return answer.strip()