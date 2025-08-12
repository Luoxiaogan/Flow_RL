# Workflow ID: high_level_math_ganluo_4_0
# Benchmark: high_level_math_ganluo
# Data Indices: [10]

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

        # Step 1: Extract key components and constraints from the problem
        extraction_instruction = (
            "Extract all mathematical components, constraints, and requirements from the problem. "
            "Identify variables, equations, functions, and any special conditions. "
            "Organize the information in a structured format for further analysis."
        )
        problem_structure = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches in parallel
        approach_instructions = [
            f"Using algebraic techniques, solve the problem based on the following structure: {problem_structure}. "
            "Focus on equations, inequalities, and functional relationships.",

            f"Using geometric reasoning, analyze the problem based on the following structure: {problem_structure}. "
            "Consider visual representations, coordinate geometry, and spatial relationships.",

            f"Using combinatorial or number-theoretic methods, address the problem based on the following structure: {problem_structure}. "
            "Focus on counting principles, modular arithmetic, and divisibility conditions."
        ]
        approaches = await asyncio.gather(
            *[self.generate(instruction=instr, context=self.problem_text) for instr in approach_instructions]
        )

        # Step 3: Refine and validate each approach
        refine_instructions = [
            f"Critique and improve the following solution approach: {approach}. "
            "Ensure it satisfies all constraints, simplify expressions, and verify edge cases."
            for approach in approaches
        ]
        refined_approaches = await asyncio.gather(
            *[self.revise(instruction=instr, context=approach) for instr, approach in zip(refine_instructions, approaches)]
        )

        # Step 4: Ensemble decision-making to select the best solution
        ensemble_instruction = (
            "Evaluate the following refined approaches and select the most correct, elegant, and complete solution. "
            "If multiple approaches are valid, synthesize their insights into a unified solution."
        )
        final_solution = await self.ensemble(instruction=ensemble_instruction, contexts=refined_approaches)

        # Step 5: Extract and format the final answer
        answer_extraction_instruction = (
            f"From the final solution: {final_solution}, extract the answer in the required format. "
            "Ensure it adheres to the problem's output specifications (e.g., fractions, radicals)."
        )
        final_answer = await self.generate(instruction=answer_extraction_instruction, context=self.problem_text)

        return final_answer