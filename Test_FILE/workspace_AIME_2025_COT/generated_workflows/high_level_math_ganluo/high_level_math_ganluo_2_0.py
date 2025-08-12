# Workflow ID: high_level_math_ganluo_2_0
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

        # Step 1: Extract key information (numerical values, geometric relationships)
        extracted_info = await self.generate(
            instruction="Extract all numerical values, geometric relationships, and constraints from the problem. "
                        "Include segment lengths, areas, and any transformations like reflections. "
                        "Format the output as a structured list for clarity.",
            context=self.problem_text
        )

        # Step 2: Analyze the extracted information to derive intermediate results
        analysis_task_1 = self.generate(
            instruction=f"Using the extracted information: {extracted_info}, "
                        "compute the coordinates or positions of all points mentioned in the problem. "
                        "Include details about reflections and their effects on point positions.",
            context=self.problem_text
        )
        analysis_task_2 = self.generate(
            instruction=f"Using the extracted information: {extracted_info}, "
                        "analyze the given area of quadrilateral DEGF and determine how it relates to the overall geometry. "
                        "Identify any proportional relationships or formulas that can be applied.",
            context=self.problem_text
        )

        # Execute analyses in parallel
        analysis_results = await asyncio.gather(analysis_task_1, analysis_task_2)

        # Step 3: Synthesize results from parallel analyses
        synthesized_solution = await self.ensemble(
            instruction="Combine the results from the two analyses. "
                        "Ensure consistency between the computed point positions and the area relationships. "
                        "Prepare a unified description of the geometric configuration.",
            contexts=analysis_results
        )

        # Step 4: Compute the final answer (area of heptagon AFNBCEM)
        final_answer = await self.generate(
            instruction=f"Based on the synthesized solution: {synthesized_solution}, "
                        "compute the area of heptagon AFNBCEM. "
                        "Use all available geometric relationships and ensure the calculation is precise.",
            context=self.problem_text
        )

        # Optional: Refine and verify the solution
        refined_solution = await self.revise(
            instruction="Critique the final solution for correctness and completeness. "
                        "Ensure all constraints and conditions from the problem are satisfied. "
                        "Refine the explanation if necessary.",
            context=final_answer
        )

        return refined_solution