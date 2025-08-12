# Workflow ID: high_level_math_ganluo_11_0
# Benchmark: high_level_math_ganluo
# Data Indices: [29]

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

        # Step 1: Extract and Understand Key Components
        extract_instruction = (
            "Extract and summarize the key components of the problem, including the function definition, "
            "constraints, and what is being asked. Focus on identifying any symmetries, patterns, or special properties."
        )
        extracted_info = await self.generate(instruction=extract_instruction, context=self.problem_text)

        # Step 2: Analyze Function Behavior
        analyze_instruction = (
            f"Given the extracted information: {extracted_info}\n"
            "Analyze the behavior of the function. Specifically, use calculus to determine the critical points "
            "where the function achieves minima. Consider the constraints provided in the problem."
        )
        function_analysis = await self.generate(instruction=analyze_instruction, context=self.problem_text)

        # Step 3: Generate Candidate Solutions
        generate_candidates_instruction = (
            f"Based on the analysis: {function_analysis}\n"
            "Propose candidate values of the parameter k that satisfy the problem's conditions. "
            "Consider multiple approaches and ensure all constraints are met."
        )
        candidates = await self.generate(instruction=generate_candidates_instruction, context=self.problem_text)

        # Step 4: Validate and Refine Solutions
        refine_instruction = (
            f"Review the proposed candidates: {candidates}\n"
            "Validate each candidate against the problem's constraints. Refine the list if necessary."
        )
        refined_candidates = await self.revise(instruction=refine_instruction, context=candidates)

        # Step 5: Summarize and Ensemble Results
        summary_instruction = (
            "Summarize the refined candidate solutions and their validation status. "
            "Ensure the final result is concise and directly answers the problem."
        )
        final_summary = await self.summarize(instruction=summary_instruction, context=refined_candidates)

        # Optional: If multiple solution paths exist, ensemble them
        ensemble_instruction = (
            "Compare and synthesize the results from different solution paths. "
            "Select the most robust and complete solution."
        )
        final_result = await self.ensemble(instruction=ensemble_instruction, contexts=[final_summary])

        return final_result