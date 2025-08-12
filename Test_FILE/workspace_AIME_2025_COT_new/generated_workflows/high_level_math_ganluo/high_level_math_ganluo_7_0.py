# Workflow ID: high_level_math_ganluo_7_0
# Benchmark: high_level_math_ganluo
# Data Indices: [1]

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

        # Step 1: Extract key information and decompose the problem
        extraction_instruction = (
            "Extract all key mathematical entities, relationships, and constraints from the problem. "
            "Include numerical values, geometric configurations, algebraic expressions, and any other relevant details. "
            "Organize the information in a structured format."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple solution approaches
        algebraic_instruction = (
            f"Using the extracted information: {extracted_info}, develop an algebraic solution approach. "
            "Focus on equations, inequalities, and functional relationships. "
            "Provide step-by-step reasoning."
        )
        geometric_instruction = (
            f"Using the extracted information: {extracted_info}, develop a geometric solution approach. "
            "Focus on coordinate geometry, synthetic geometry, and area/volume calculations. "
            "Provide step-by-step reasoning."
        )
        combinatorial_instruction = (
            f"Using the extracted information: {extracted_info}, develop a combinatorial solution approach. "
            "Focus on counting principles, recursive structures, and probabilistic methods. "
            "Provide step-by-step reasoning."
        )

        # Execute approaches in parallel
        algebraic_solution, geometric_solution, combinatorial_solution = await asyncio.gather(
            self.generate(instruction=algebraic_instruction, context=self.problem_text),
            self.generate(instruction=geometric_instruction, context=self.problem_text),
            self.generate(instruction=combinatorial_instruction, context=self.problem_text)
        )

        # Step 3: Refine each solution approach
        refine_instruction_template = (
            "Critique and refine the following solution approach. "
            "Ensure logical consistency, mathematical rigor, and adherence to the problem's constraints. "
            "Provide detailed feedback and improvements."
        )
        refined_algebraic = await self.revise(instruction=refine_instruction_template, context=algebraic_solution)
        refined_geometric = await self.revise(instruction=refine_instruction_template, context=geometric_solution)
        refined_combinatorial = await self.revise(instruction=refine_instruction_template, context=combinatorial_solution)

        # Step 4: Synthesize the best solution
        synthesis_instruction = (
            "Compare and synthesize the following refined solution approaches into a single cohesive solution. "
            "Select the most robust and elegant approach that satisfies all problem constraints. "
            "Provide justification for your choice."
        )
        final_solution = await self.ensemble(
            instruction=synthesis_instruction,
            contexts=[refined_algebraic, refined_geometric, refined_combinatorial]
        )

        # Step 5: Verify and summarize the final solution
        summary_instruction = (
            "Summarize the final solution in a clear and concise manner. "
            "Ensure all parts of the problem are addressed and the solution satisfies all constraints. "
            "Highlight key insights and reasoning steps."
        )
        verified_solution = await self.summarize(instruction=summary_instruction, context=final_solution)

        return verified_solution