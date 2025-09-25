# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.verifier = operator.Verifier(self.llm, self.problem_text)
        self.refiner = operator.Refiner(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio

        # Step 1: Extract key components of the problem
        extraction_instruction = """
        Analyze the provided problem statement and extract:
        1. All mathematical objects, variables, and constants mentioned
        2. The specific conditions or constraints given
        3. The ultimate goal or what is being asked
        4. Any symmetries, patterns, or transformations that might be useful
        Provide the extracted information in a structured format.
        """
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches
        approach1_instruction = f"""
        Given the extracted information: {extracted_info}
        Develop a detailed step-by-step solution approach. Focus on:
        - Identifying key theorems or principles that apply
        - Breaking the problem into smaller sub-problems if possible
        - Using precise mathematical reasoning
        Present the solution in a clear, logically structured format.
        """
        approach1 = await self.generate(instruction=approach1_instruction, context=self.problem_text)

        approach2_instruction = f"""
        Given the extracted information: {extracted_info}
        Explore an alternative solution approach that differs from the first approach. Focus on:
        - Using different mathematical techniques or perspectives
        - Leveraging symmetry or transformation strategies if applicable
        - Ensuring the solution is rigorous and complete
        Present the solution in a clear, logically structured format.
        """
        approach2 = await self.generate(instruction=approach2_instruction, context=self.problem_text)

        # Step 3: Ensemble decision to select the best approach
        ensemble_instruction = """
        Evaluate the two proposed solutions and select the most rigorous and complete one. 
        Consider factors such as:
        - Logical consistency
        - Mathematical correctness
        - Completeness of justification
        Provide the reasons for your selection and return the best solution.
        """
        selected_solution = await self.ensemble(instruction=ensemble_instruction, contexts=[approach1, approach2])

        # Step 4: Verify the selected solution
        verification_instruction = """
        Perform a meticulous verification of the selected solution. Check for:
        - Errors in logical reasoning
        - Inconsistencies or omissions in the proof
        - Validity of all mathematical claims
        Provide a detailed report of any issues found and classify the solution as:
        - Valid: No errors found
        - Invalid: Contains critical errors
        - Partial: Some issues exist but not critical
        """
        verification = await self.verifier(instruction=verification_instruction, context=selected_solution)

        # Step 5: Refine the solution based on verification feedback
        refinement_instruction = f"""
        Based on the verification feedback: {verification}
        Improve the solution by addressing any identified issues. Focus on:
        - Correcting logical inconsistencies
        - Completing missing justifications
        - Ensuring mathematical rigor
        Provide the refined solution along with a description of the improvements made.
        """
        refined_solution = await self.refiner(
            instruction=refinement_instruction,
            context=selected_solution,
            verification_feedback=str(verification)
        )

        # Step 6: Finalize the solution
        final_instruction = """
        Ensure that the refined solution is complete, rigorous, and addresses all aspects of the problem. 
        If necessary, summarize the key steps and conclusions in a clear manner.
        """
        final_solution = await self.generate(instruction=final_instruction, context=refined_solution["refined_solution"])

        return final_solution