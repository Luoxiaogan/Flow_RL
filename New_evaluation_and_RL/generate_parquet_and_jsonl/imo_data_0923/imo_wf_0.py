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

        # Step 1: Understand the Problem
        problem_understanding = await self.generate(
            instruction="Thoroughly analyze the problem statement. Identify the key components, constraints, and what is being asked. "
                          "Break down the problem into smaller, manageable parts. Provide a structured summary of the problem.",
            context=self.problem_text
        )

        # Step 2: Generate Multiple Solution Approaches
        approach1 = await self.generate(
            instruction="Given the problem understanding, propose a detailed solution approach. Focus on creative insights and advanced problem-solving techniques. "
                          "Include step-by-step reasoning and highlight potential challenges.",
            context=problem_understanding
        )

        approach2 = await self.generate(
            instruction="Given the problem understanding, propose an alternative detailed solution approach. Focus on creative insights and advanced problem-solving techniques. "
                          "Include step-by-step reasoning and highlight potential challenges.",
            context=problem_understanding
        )

        # Step 3: Ensemble Decision (Select Best Approach)
        best_approach = await self.ensemble(
            instruction="Evaluate the two proposed solution approaches. Compare their strengths and weaknesses. "
                         "Select the most promising approach based on mathematical rigor and feasibility. Provide a justification for your choice.",
            contexts=[approach1, approach2]
        )

        # Step 4: Generate Initial Solution Based on Best Approach
        initial_solution = await self.generate(
            instruction=f"Based on the selected approach: {best_approach}, generate a detailed mathematical solution. "
                         "Include all necessary proofs, justifications, and intermediate steps. Ensure the solution is complete and rigorous.",
            context=problem_understanding
        )

        # Step 5: Verify the Initial Solution
        verification = await self.verifier(
            instruction="Carefully verify the generated solution. Check for logical consistency, mathematical correctness, and rigor. "
                         "Identify any errors, gaps, or ambiguities in the reasoning. Provide a detailed list of findings.",
            context=initial_solution
        )

        # Step 6: Refine the Solution Based on Verification Feedback
        if verification["verdict"] != "valid":
            refinement = await self.refiner(
                instruction=f"Based on the verification feedback: {verification}, systematically refine the solution. "
                             "Address all identified issues and improve the mathematical rigor of the solution.",
                context=initial_solution,
                verification_feedback=str(verification)
            )
            refined_solution = refinement["refined_solution"]
        else:
            refined_solution = initial_solution

        # Step 7: Final Solution
        final_solution = refined_solution

        return final_solution