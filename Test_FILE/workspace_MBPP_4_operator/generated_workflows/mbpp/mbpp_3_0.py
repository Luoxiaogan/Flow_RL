# Workflow ID: mbpp_3_0
# Benchmark: mbpp
# Data Indices: [146]

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
        
        # Step 1: Extract Function Name and Signature
        function_info = await self.generate(
            instruction="""Extract the function name and its parameters from the assert statements. 
            Provide the function signature in the format 'def function_name(args):'.""",
            context=""
        )
        
        # Step 2: Understand Task Requirements
        task_summary = await self.generate(
            instruction="""Parse the natural language description to understand the task requirements. 
            Summarize the core operations needed (e.g., loops, conditionals).""",
            context=function_info
        )
        
        # Step 3: Explore Solution Strategies
        solution_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Create a straightforward implementation based on:
                {task_summary}""",
                context=task_summary
            ),
            self.generate(
                instruction=f"""Explore an optimized algorithm based on:
                {task_summary}""",
                context=task_summary
            )
        )
        
        # Step 4: Validate and Refine Solutions
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine the solution against the test cases.",
                context=solution
            ) for solution in solution_strategies]
        )
        
        # Step 5: Synthesize Best Solution
        final_solution = await self.ensemble(
            instruction="Select the most robust and efficient solution.",
            contexts_list=refined_solutions
        )
        
        return final_solution