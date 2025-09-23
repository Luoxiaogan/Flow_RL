# Workflow ID: mbpp_47_0
# Benchmark: mbpp
# Data Indices: [172]

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
        
        # Stage 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract the function name from test cases and classify the problem type.
            Identify key operations (e.g., list traversal, substring matching) and required imports.
            Provide structured output with:
            - Function name
            - Problem type
            - Key operations
            - Required imports""",
            context=""
        )
        
        # Stage 2: Intermediate Representation
        intermediate = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a high-level plan or pseudocode:
            - Outline the function structure
            - Describe the logic step-by-step
            - Include necessary imports""",
            context=analysis
        )
        
        # Stage 3: Code Generation
        code = await self.generate(
            instruction=f"""Translate the intermediate representation into executable Python code:
            Intermediate Representation:
            {intermediate}
            
            Ensure:
            - Proper indentation
            - All necessary imports
            - Adherence to Python syntax""",
            context=intermediate
        )
        
        # Stage 4: Validation and Refinement
        validation = await self.generate(
            instruction=f"""Validate the generated code against test cases:
            Generated Code:
            {code}
            
            Report any errors or mismatches.""",
            context=code
        )
        
        refined_code = code
        if "error" in validation.lower():
            refined_code = await self.revise(
                instruction=f"""Revise the code to address issues:
                Issues:
                {validation}
                
                Ensure all test cases pass.""",
                context=code
            )
        
        # Stage 5: Final Assembly
        final_code = await self.ensemble(
            instruction=f"""Combine insights from previous steps to produce the final, polished code:
            Initial Code:
            {code}
            
            Refined Code:
            {refined_code}
            
            Ensure the solution is complete, optimized, and adheres to all requirements.""",
            contexts_list=[code, refined_code]
        )
        
        return final_code