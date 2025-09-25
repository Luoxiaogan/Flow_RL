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
        Analyze the problem and extract the following:
        1. All mathematical objects, entities, and relationships mentioned in the problem (e.g., figures, numbers, equations, constraints).
        2. The specific question being asked (e.g., "Determine the minimum number...", "Find all possible values...").
        3. The conditions or constraints that must be satisfied by the solution.
        4. Any implicit assumptions or properties that can be inferred from the problem statement.
        Ensure the extracted information is comprehensive and precise.
        """
        extracted_components = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches
        approach1_instruction = f"""
        Given the extracted components: {extracted_components}
        Generate a detailed solution approach for the problem. Focus on:
        - Breaking the problem into smaller, manageable sub-problems.
        - Exploring creative mathematical techniques (algebraic, geometric, combinatorial, etc.).
        - Including step-by-step reasoning and justification for each step.
        - Ensuring all conditions and constraints are explicitly addressed.
        """
        approach1 = await self.generate(instruction=approach1_instruction, context=self.problem_text)

        approach2_instruction = f"""
        Given the extracted components: {extracted_components}
        Generate an alternative detailed solution approach for the problem. Focus on:
        - Using a different mathematical framework or strategy compared to the first approach.
        - Highlighting any unique insights or techniques that could lead to a novel solution.
        - Ensuring all conditions and constraints are explicitly addressed.
        - Including step-by-step reasoning and justification for each step.
        """
        approach2 = await self.generate(instruction=approach2_instruction, context=self.problem_text)

        # Step 3: Ensemble decision to select the best approach
        ensemble_instruction = """
        Evaluate the two solution approaches provided. Select the best one based on the following criteria:
        1. Completeness of the solution (does it fully address the problem?).
        2. Logical consistency and rigor of the reasoning.
        3. Clarity and precision of the explanation.
        4. Adherence to all problem constraints and conditions.
        Provide the selected approach as the final solution.
        """
        selected_approach = await self.ensemble(
            instruction=ensemble_instruction,
            contexts=[approach1, approach2]
        )

        # Step 4: Verify the selected approach
        verification_instruction = """
        Use rigorous mathematical reasoning to verify the selected solution. Check for:
        - Logical validity of each step in the solution.
        - Accuracy of any calculations or derivations.
        - Correctness of any theorems or properties applied.
        - Completeness of the solution (does it answer the question?).
        Provide a detailed verdict and list any issues found.
        """
        verification = await self.verifier(
            instruction=verification_instruction,
            context=selected_approach
        )

        # Step 5: Refine the solution based on verification feedback
        refinement_instruction = f"""
        Based on the verification findings: {verification}
        Refine the selected solution to address any identified issues. Focus on:
        - Correcting mathematical errors or logical gaps.
        - Improving the clarity and precision of the explanation.
        - Ensuring all conditions and constraints are explicitly satisfied.
        Provide the refined solution as the final output.
        """
        refinement = await self.refiner(
            instruction=refinement_instruction,
            context=selected_approach,
            verification_feedback=str(verification)
        )

        return refinement["refined_solution"]