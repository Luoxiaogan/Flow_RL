# Workflow ID: high_level_math_ganluo_2_0
# Benchmark: high_level_math_ganluo
# Data Indices: [23]

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

        # Step 1: Extract key elements of the problem
        extraction_instruction = """
        Extract all key elements of the problem, including:
        - Variables and their domains
        - Equations or functions involved
        - Constraints or conditions
        - What is being asked to solve
        Organize the information clearly for further analysis.
        """
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate multiple candidate solutions
        algebraic_instruction = f"""
        Solve the problem using an algebraic approach. Consider:
        - Simplifying expressions
        - Solving equations step-by-step
        - Verifying intermediate results
        Use the following extracted information: {extracted_info}
        """
        geometric_instruction = f"""
        Solve the problem using a geometric approach. Consider:
        - Visualizing the problem
        - Identifying symmetries or patterns
        - Applying geometric theorems
        Use the following extracted information: {extracted_info}
        """
        combinatorial_instruction = f"""
        Solve the problem using a combinatorial approach. Consider:
        - Counting possibilities
        - Recursive reasoning
        - Generating functions if applicable
        Use the following extracted information: {extracted_info}
        """

        # Execute approaches in parallel
        algebraic_solution, geometric_solution, combinatorial_solution = await asyncio.gather(
            self.generate(instruction=algebraic_instruction, context=self.problem_text),
            self.generate(instruction=geometric_instruction, context=self.problem_text),
            self.generate(instruction=combinatorial_instruction, context=self.problem_text)
        )

        # Step 3: Revise and refine each solution
        revise_instruction_template = """
        Critique and refine the following solution:
        - Check for mathematical correctness
        - Ensure all constraints are satisfied
        - Improve clarity and presentation
        Solution: {}
        """
        revised_algebraic = await self.revise(instruction=revise_instruction_template.format(algebraic_solution), context=self.problem_text)
        revised_geometric = await self.revise(instruction=revise_instruction_template.format(geometric_solution), context=self.problem_text)
        revised_combinatorial = await self.revise(instruction=revise_instruction_template.format(combinatorial_solution), context=self.problem_text)

        # Step 4: Synthesize the best solution
        ensemble_instruction = """
        Evaluate and synthesize the following refined solutions:
        - Compare their correctness and completeness
        - Identify complementary insights
        - Select the most robust and elegant solution
        Solutions:
        1. Algebraic: {}
        2. Geometric: {}
        3. Combinatorial: {}
        """
        final_solution = await self.ensemble(
            instruction=ensemble_instruction.format(revised_algebraic, revised_geometric, revised_combinatorial),
            contexts=[revised_algebraic, revised_geometric, revised_combinatorial]
        )

        # Step 5: Summarize the final solution
        summarize_instruction = """
        Condense the final solution into a clear and concise form:
        - Highlight the key steps
        - Verify it satisfies all problem constraints
        - Present the answer in the required format
        Final Solution: {}
        """
        summary = await self.summarize(instruction=summarize_instruction.format(final_solution), context=self.problem_text)

        return summary