# Workflow ID: high_level_math_ganluo_29_0
# Benchmark: high_level_math_ganluo
# Data Indices: [17]

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

        # Step 1: Extract problem components and constraints
        extraction_instruction = (
            "Extract all key mathematical objects, relationships, and constraints from the problem. "
            "Identify the type of problem (e.g., combinatorics, geometry) and list any specific rules or conditions."
        )
        extracted_info = await self.generate(instruction=extraction_instruction, context=self.problem_text)

        # Step 2: Generate potential solution approaches
        generation_instruction = (
            f"Based on the extracted information: {extracted_info}, generate multiple solution approaches. "
            "Consider different cases or strategies that could lead to a valid solution. "
            "For example, in combinatorial problems, consider casework or recursive structures."
        )
        approaches = await self.generate(instruction=generation_instruction, context=self.problem_text)

        # Step 3: Parallel exploration of cases
        cases = approaches.split("\n")  # Split into individual cases
        tasks = []
        for case in cases:
            case_instruction = (
                f"Solve the problem using the following approach: {case}. "
                "Ensure all constraints are satisfied and provide a detailed reasoning process."
            )
            tasks.append(self.generate(instruction=case_instruction, context=self.problem_text))
        case_results = await asyncio.gather(*tasks)

        # Step 4: Evaluate and synthesize results
        ensemble_instruction = (
            "Compare the results from different cases and select the most promising solution. "
            "Ensure that the chosen solution satisfies all constraints and is mathematically sound. "
            "If multiple solutions are valid, combine their insights."
        )
        best_solution = await self.ensemble(instruction=ensemble_instruction, contexts=case_results)

        # Step 5: Refine and finalize the solution
        refinement_instruction = (
            "Review the selected solution for clarity, correctness, and completeness. "
            "Address any ambiguities or errors, and ensure the solution is presented in a rigorous format."
        )
        refined_solution = await self.revise(instruction=refinement_instruction, context=best_solution)

        # Step 6: Summarize the final result
        summary_instruction = (
            "Condense the solution into a concise format while preserving all key insights and steps. "
            "Ensure the summary is easy to follow and verifies the correctness of the solution."
        )
        final_summary = await self.summarize(instruction=summary_instruction, context=refined_solution)

        return final_summary