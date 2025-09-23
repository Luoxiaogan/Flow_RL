# Workflow ID: gsm8k_22_0
# Benchmark: gsm8k
# Data Indices: [58, 245]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Step 1: Problem Analysis
        analysis_instruction = """Extract all numerical values, units, entities, and relationships from the problem. 
        Identify what the question is asking for and any constraints provided."""
        problem_analysis = await self.generate(instruction=analysis_instruction, context="")

        # Step 2: Solution Planning
        planning_instruction = f"""Based on the following analysis:
        {problem_analysis}
        
        Plan the sequence of operations needed to solve the problem. 
        Include all necessary calculations and intermediate steps."""
        solution_plan = await self.generate(instruction=planning_instruction, context=problem_analysis)

        # Step 3: Calculation Execution
        execution_instruction = f"""Execute the following solution plan step-by-step:
        {solution_plan}
        
        Show all calculations and intermediate results clearly."""
        initial_solution = await self.generate(instruction=execution_instruction, context=solution_plan)

        # Step 4: Validation and Refinement
        validation_instruction = f"""Validate the following solution:
        {initial_solution}
        
        Check for calculation errors, ensure the answer makes sense, and refine if necessary."""
        validated_solution = await self.revise(instruction=validation_instruction, context=initial_solution)

        # Optional: Ensemble for multiple solution paths
        alternative_solutions = await asyncio.gather(
            self.generate(instruction="Solve the problem using an alternative method.", context=""),
            self.generate(instruction="Solve the problem using another alternative method.", context="")
        )
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=[validated_solution] + alternative_solutions
        )

        # Step 5: Summarize Final Answer
        summary_instruction = f"""Summarize the final solution:
        {final_solution}
        
        Provide only the numerical answer."""
        final_answer = await self.summarize(instruction=summary_instruction, context=final_solution)

        return final_answer