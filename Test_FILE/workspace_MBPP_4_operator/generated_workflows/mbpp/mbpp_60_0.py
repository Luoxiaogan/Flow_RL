# Workflow ID: mbpp_60_0
# Benchmark: mbpp
# Data Indices: [304, 6]

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

        # Phase 1: Problem Analysis
        analysis_instruction = """Extract key information from the problem:
        - Function name from assert statements
        - Input/output types and descriptions
        - Requirements and constraints
        Format as structured JSON."""
        problem_analysis = await self.generate(instruction=analysis_instruction, context="")

        # Phase 2: Solution Generation
        solution_instruction = f"""Generate a Python function based on the analysis:
        {problem_analysis}
        Ensure:
        - Proper function name and signature
        - Complete imports at the top
        - Correct logic implementation
        - Passes provided test cases"""
        initial_solution = await self.generate(instruction=solution_instruction, context=problem_analysis)

        # Phase 3: Code Validation and Refinement
        validation_instruction = """Validate the generated code:
        - Check if it passes all test cases
        - Identify any logical errors or edge cases
        Provide feedback for improvement."""
        validation_feedback = await self.generate(instruction=validation_instruction, context=initial_solution)

        if "error" in validation_feedback.lower():
            refined_solution = await self.revise(
                instruction=f"Fix issues based on feedback: {validation_feedback}",
                context=initial_solution
            )
        else:
            refined_solution = initial_solution

        # Phase 4: Final Output
        final_instruction = """Ensure the code is complete and well-formatted:
        - Proper indentation
        - All necessary imports
        - Clean syntax
        Return the final Python code."""
        final_code = await self.revise(instruction=final_instruction, context=refined_solution)

        return final_code