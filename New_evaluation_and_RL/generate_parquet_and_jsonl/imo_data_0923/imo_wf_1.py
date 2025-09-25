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

        # Step 1: Extract all key components and constraints
        extraction_instruction = """
        Analyze the problem statement and extract all key mathematical concepts, constraints, and relationships. 
        Identify any numerical values, geometric properties, algebraic expressions, or logical conditions mentioned.
        Create a structured summary of the problem for subsequent reasoning steps.
        """
        extracted_components = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches in parallel
        approach1_instruction = f"""
        Given the extracted components: {extracted_components}
        Provide a detailed solution approach by breaking down the problem into manageable sub-problems. 
        Use rigorous mathematical reasoning to outline each step and ensure completeness.
        """
        approach2_instruction = f"""
        Given the extracted components: {extracted_components}
        Generate an alternative solution approach by exploring different mathematical techniques or perspectives. 
        Ensure that this approach is distinct from the first and addresses the same core problem.
        """
        approach3_instruction = f"""
        Given the extracted components: {extracted_components}
        Propose a third solution approach, focusing on a unique angle or method not covered in the first two approaches. 
        Justify why this approach is valid and how it contributes to solving the problem.
        """

        # Execute the three approaches in parallel
        approach1 = self.generate(instruction=approach1_instruction, context=self.problem_text)
        approach2 = self.generate(instruction=approach2_instruction, context=self.problem_text)
        approach3 = self.generate(instruction=approach3_instruction, context=self.problem_text)

        approaches = await asyncio.gather(approach1, approach2, approach3)

        # Step 3: Ensemble decision to select the best approach
        ensemble_instruction = f"""
        Given the extracted components: {extracted_components}
        Evaluate the following solution approaches: {approaches[0]}, {approaches[1]}, {approaches[2]}.
        Compare them based on mathematical rigor, completeness, clarity, and relevance to the problem constraints. 
        Select the most robust and comprehensive solution approach.
        """
        selected_approach = await self.ensemble(instruction=ensemble_instruction, contexts=approaches)

        # Step 4: Verify the selected solution approach
        verification_instruction = f"""
        Given the extracted components: {extracted_components}
        Analyze the selected solution approach: {selected_approach}.
        Perform a rigorous mathematical verification to ensure correctness, logical consistency, and completeness. 
        Identify any gaps, ambiguities, or errors in reasoning.
        """
        verification_result = await self.verifier(instruction=verification_instruction, context=selected_approach)

        # Step 5: Refine the solution based on verification feedback
        refinement_instruction = f"""
        Given the extracted components: {extracted_components}
        Analyze the verification feedback: {verification_result}.
        Improve the selected solution approach by addressing any identified issues or gaps. 
        Ensure that the refined solution is mathematically rigorous and satisfies all problem constraints.
        """
        refinement_result = await self.refiner(
            instruction=refinement_instruction,
            context=selected_approach,
            verification_feedback=str(verification_result)
        )

        # Final solution is the refined solution
        refined_solution = refinement_result["refined_solution"]
        return refined_solution