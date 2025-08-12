# Workflow ID: high_level_math_ganluo_1_0
# Benchmark: high_level_math_ganluo
# Data Indices: [25]

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

        # Step 1: Extract and Analyze Problem Components
        extraction_instruction = (
            "Analyze the problem statement thoroughly. Identify all key components, "
            "including numerical values, constraints, and relationships. Provide a structured breakdown."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate Multiple Candidate Solutions
        approach_1_instruction = (
            f"Using the extracted information: {extracted_info}\n"
            "Develop a combinatorial approach to solve the problem. Consider all possible configurations "
            "and count valid arrangements systematically."
        )
        approach_2_instruction = (
            f"Using the extracted information: {extracted_info}\n"
            "Develop a geometric approach to solve the problem. Exploit symmetry and geometric properties "
            "to simplify the counting process."
        )

        # Parallel execution for independent approaches
        results = await asyncio.gather(
            self.generate(instruction=approach_1_instruction, context=self.problem_text),
            self.generate(instruction=approach_2_instruction, context=self.problem_text)
        )
        combinatorial_solution, geometric_solution = results

        # Step 3: Refine and Validate Candidate Solutions
        refine_instruction = (
            "Critique the provided solution. Check for mathematical correctness, logical consistency, "
            "and adherence to problem constraints. Suggest improvements if necessary."
        )
        refined_combinatorial = await self.revise(instruction=refine_instruction, context=combinatorial_solution)
        refined_geometric = await self.revise(instruction=refine_instruction, context=geometric_solution)

        # Step 4: Synthesize Results Using Ensemble
        ensemble_instruction = (
            "Compare the two refined solutions. Evaluate their mathematical rigor, clarity, and efficiency. "
            "Select the most robust and accurate solution, or combine their strengths into a single answer."
        )
        final_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts=[refined_combinatorial, refined_geometric]
        )

        # Step 5: Summarize the Final Solution
        summarize_instruction = (
            "Condense the final solution into a concise and clear format. Ensure it includes all key steps, "
            "reasoning, and the final answer."
        )
        summary = await self.summarize(instruction=summarize_instruction, context=final_solution)

        return summary