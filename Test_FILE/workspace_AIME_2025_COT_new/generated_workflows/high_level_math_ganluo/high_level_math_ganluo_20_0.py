# Workflow ID: high_level_math_ganluo_20_0
# Benchmark: high_level_math_ganluo
# Data Indices: [19]

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
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio

        # Step 1: Extract key information from the problem
        extraction_instruction = (
            "Extract all geometric entities, relationships, and constraints from the problem text. "
            "Include details about points, angles, lines, circles, and any specific calculations required. "
            "Provide the extracted information in a structured format."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Develop a solution strategy
        strategy_instruction = (
            f"Given the following extracted information: {extracted_info}\n"
            "Analyze the geometric relationships and develop a step-by-step plan to solve the problem. "
            "Include any relevant theorems, properties, or formulas that will be used. "
            "Focus on how to compute the required quantities (e.g., arc measures)."
        )
        strategy = await self.generate(instruction=strategy_instruction, context=self.problem_text)

        # Step 3: Parallel computation of sub-problems
        arc_de_instruction = (
            f"Using the strategy: {strategy}\n"
            "Compute the measure of arc DE on the circumcircle of triangle DEF. "
            "Provide the result in degrees."
        )
        arc_hj_instruction = (
            f"Using the strategy: {strategy}\n"
            "Compute the measure of arc HJ on the circumcircle of triangle DEF. "
            "Provide the result in degrees."
        )
        arc_fg_instruction = (
            f"Using the strategy: {strategy}\n"
            "Compute the measure of arc FG on the circumcircle of triangle DEF. "
            "Provide the result in degrees."
        )
        arc_results = await asyncio.gather(
            self.generate(instruction=arc_de_instruction, context=self.problem_text),
            self.generate(instruction=arc_hj_instruction, context=self.problem_text),
            self.generate(instruction=arc_fg_instruction, context=self.problem_text)
        )

        # Step 4: Combine results and compute the final answer
        combine_instruction = (
            f"Given the following arc measures: DE = {arc_results[0]}, HJ = {arc_results[1]}, FG = {arc_results[2]}\n"
            "Compute the final result using the formula: DE + 2 * HJ + 3 * FG. "
            "Ensure the calculation is accurate and provide the final answer."
        )
        combined_result = await self.generate(instruction=combine_instruction, context=self.problem_text)

        # Step 5: Verify and refine the solution
        verification_instruction = (
            f"Verify the solution: {combined_result}\n"
            "Check if it satisfies all constraints and makes mathematical sense. "
            "If necessary, suggest refinements or corrections."
        )
        final_solution = await self.revise(instruction=verification_instruction, context=combined_result)

        return final_solution