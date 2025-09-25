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

        # Step 1: Initial Analysis
        analysis_instruction = (
            "Perform a detailed analysis of the problem statement. Identify all key components, "
            "constraints, and relationships between elements. Classify the problem type (e.g., combinatorial, geometric, algebraic) "
            "and outline potential strategies for solving it."
        )
        analysis = await self.generate(instruction=analysis_instruction, context=self.problem_text)

        # Step 2: Generate Multiple Solution Approaches
        approach1_instruction = (
            "Based on the analysis, propose a first mathematical approach to solve the problem. "
            "Break down the problem into smaller sub-problems and describe the steps required to solve each. "
            "Include detailed reasoning and justification for each step."
        )
        approach2_instruction = (
            "Based on the analysis, propose a second distinct mathematical approach to solve the problem. "
            "Ensure that this approach is fundamentally different from the first one. "
            "Detail the reasoning behind this alternative method."
        )
        approach1 = await self.generate(instruction=approach1_instruction, context=analysis)
        approach2 = await self.generate(instruction=approach2_instruction, context=analysis)

        # Step 3: Ensemble Decision
        ensemble_instruction = (
            "Evaluate and compare the two proposed solutions. Determine which approach is more robust, "
            "mathematically sound, and efficient. Justify your decision based on the strengths and weaknesses of each method."
        )
        selected_approach = await self.ensemble(instruction=ensemble_instruction, contexts=[approach1, approach2])

        # Step 4: Generate the Solution
        solution_instruction = (
            "Using the selected approach, generate a complete mathematical solution to the problem. "
            "Ensure that all steps are clearly explained, and include rigorous proofs and justifications for each claim. "
            "Verify that the solution satisfies all conditions and constraints mentioned in the problem statement."
        )
        solution = await self.generate(instruction=solution_instruction, context=selected_approach)

        # Step 5: Verify the Solution
        verification_instruction = (
            "Carefully verify the generated solution. Check for any logical inconsistencies, errors, or gaps in reasoning. "
            "Provide a detailed assessment of the solution's validity, including any potential issues or improvements."
        )
        verification = await self.verifier(instruction=verification_instruction, context=solution)

        # Step 6: Refine the Solution if Necessary
        refinement_instruction = (
            "If the verification indicates any issues or weaknesses, use the verification feedback to refine the solution. "
            "Address all identified problems and incorporate improvements to enhance the mathematical rigor and clarity of the solution."
        )
        refinement_feedback = verification
        if verification["verdict"] != "valid":
            refinement = await self.refiner(
                instruction=refinement_instruction,
                context=solution,
                verification_feedback=str(refinement_feedback)
            )
            refined_solution = refinement["refined_solution"]
        else:
            refined_solution = solution

        return refined_solution