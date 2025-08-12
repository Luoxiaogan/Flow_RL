# Workflow ID: high_level_math_ganluo_1_0
# Benchmark: high_level_math_ganluo
# Data Indices: [8]

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
        """
        import asyncio

        # Step 1: Extract key components and understand the problem
        extraction_instruction = (
            "Extract all mathematical components from the problem, including equations, "
            "geometric transformations, constraints, and any special conditions. Organize "
            "them in a structured format for further analysis."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches in parallel
        approach1_instruction = (
            f"Using the extracted information: {extracted_info}\n"
            "Solve the problem using an algebraic approach. Focus on manipulating equations, "
            "identifying patterns, and solving step by step. Ensure all constraints are satisfied."
        )
        approach2_instruction = (
            f"Using the extracted information: {extracted_info}\n"
            "Solve the problem using a geometric approach. Consider transformations, symmetries, "
            "and visual representations. Provide a clear explanation of each step."
        )
        approach3_instruction = (
            f"Using the extracted information: {extracted_info}\n"
            "Solve the problem using a combinatorial or number-theoretic approach. Explore recursive "
            "formulas, modular arithmetic, or counting techniques as applicable."
        )

        approaches = await asyncio.gather(
            self.generate(instruction=approach1_instruction, context=self.problem_text),
            self.generate(instruction=approach2_instruction, context=self.problem_text),
            self.generate(instruction=approach3_instruction, context=self.problem_text)
        )

        # Step 3: Refine each approach
        refinement_instruction_template = (
            "Refine the following solution: {solution}\n"
            "Check for correctness, simplify calculations, and ensure all constraints are satisfied. "
            "Address any edge cases and provide a rigorous justification for each step."
        )
        refined_approaches = await asyncio.gather(
            self.revise(instruction=refinement_instruction_template.format(solution=approaches[0]), context=approaches[0]),
            self.revise(instruction=refinement_instruction_template.format(solution=approaches[1]), context=approaches[1]),
            self.revise(instruction=refinement_instruction_template.format(solution=approaches[2]), context=approaches[2])
        )

        # Step 4: Select the best solution using Ensemble
        ensemble_instruction = (
            "Compare the following solutions and select the best one:\n"
            "1. {solution1}\n"
            "2. {solution2}\n"
            "3. {solution3}\n"
            "Evaluate based on clarity, correctness, computational simplicity, and adherence to the problem's requirements."
        )
        best_solution = await self.ensemble(
            instruction=ensemble_instruction.format(solution1=refined_approaches[0], solution2=refined_approaches[1], solution3=refined_approaches[2]),
            contexts=refined_approaches
        )

        # Step 5: Summarize the final solution
        summarization_instruction = (
            "Summarize the following solution to extract the final answer in the required format:\n"
            "{solution}\n"
            "Ensure the answer is concise and includes all necessary details."
        )
        final_answer = await self.summarize(instruction=summarization_instruction.format(solution=best_solution), context=best_solution)

        return final_answer