# Workflow ID: mbpp_42_0
# Benchmark: mbpp
# Data Indices: [241]

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
        
        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract key information from the problem:
            - Function name from the test cases
            - Input and output structure
            - Constraints or special conditions
            Provide structured output.""",
            context=""
        )
        
        # Phase 2: Solution Exploration
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Generate a solution using algorithmic logic.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Generate a solution leveraging Python's standard library.""",
                context=analysis
            )
        )
        
        best_solution = await self.ensemble(
            instruction="Select the most robust and efficient solution.",
            contexts_list=candidates
        )
        
        # Phase 3: Code Generation
        code = await self.generate(
            instruction=f"""Generate Python code based on the selected solution:
            {best_solution}
            
            Ensure:
            - Proper indentation and syntax
            - Necessary imports included
            - Function name matches test cases""",
            context=best_solution
        )
        
        # Phase 4: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the generated code against the test cases:
            {code}
            
            Identify any errors or inconsistencies.""",
            context=code
        )
        
        if "error" in validation.lower():
            refined_code = await self.revise(
                instruction=f"""Fix issues in the code:
                {validation}
                
                Ensure all test cases pass.""",
                context=code
            )
            final_code = refined_code
        else:
            final_code = code
        
        return final_code