# Workflow ID: high_level_math_ganluo_14_0
# Benchmark: high_level_math_ganluo
# Data Indices: [0]

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

        # Step 1: Extract key information from the problem
        extraction_instruction = (
            "Extract all key mathematical expressions, variables, constraints, and relationships from the problem. "
            "Focus on identifying: numerical values, equations, inequalities, conditions, and any special properties. "
            "Format the output as a structured summary."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Explore multiple solution approaches in parallel
        approach_instructions = [
            f"Using an algebraic approach, solve the problem step-by-step. Key information: {extracted_info}.",
            f"Using a combinatorial or counting approach, solve the problem step-by-step. Key information: {extracted_info}.",
            f"Using number theory techniques, solve the problem step-by-step. Key information: {extracted_info}."
        ]
        approach_contexts = [self.problem_text] * len(approach_instructions)
        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=ctx) for instr, ctx in zip(approach_instructions, approach_contexts)]
        )

        # Step 3: Refine each candidate solution
        refinement_instruction_template = (
            "Critique and refine the following solution. Ensure it satisfies all constraints, handles edge cases, "
            "and is mathematically rigorous. Provide detailed feedback and corrections if needed."
        )
        refined_solutions = await asyncio.gather(
            *[self.revise(instruction=refinement_instruction_template, context=sol) for sol in candidate_solutions]
        )

        # Step 4: Synthesize and select the best solution
        synthesis_instruction = (
            "Compare the following solutions and select the most robust, elegant, and mathematically sound one. "
            "Ensure the chosen solution satisfies all constraints and is clearly explained."
        )
        final_solution = await self.ensemble(instruction=synthesis_instruction, contexts=refined_solutions)

        # Step 5: Summarize the final solution for clarity
        summary_instruction = (
            "Condense the following solution into a concise, clear, and well-structured summary. "
            "Highlight the key steps and the final answer."
        )
        summarized_solution = await self.summarize(instruction=summary_instruction, context=final_solution)

        return summarized_solution