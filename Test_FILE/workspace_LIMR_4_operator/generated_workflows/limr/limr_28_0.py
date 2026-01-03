# Workflow ID: limr_28_0
# Benchmark: limr
# Data Indices: [294, 154]

# --- DO NOT IMPORT HERE ---
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
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one or more subfields:
            - Identify key components (e.g., numbers, variables, relationships)
            - Determine the primary mathematical domain (e.g., geometry, number theory)
            - Extract constraints and requirements
            - Suggest potential solution strategies""",
            context=""
        )

        # Phase 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Solve the problem using a geometric approach:
                - Apply coordinate geometry or trigonometric identities
                - Validate intermediate results""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Solve the problem using a number-theoretic approach:
                - Apply modular arithmetic or prime factorization
                - Validate intermediate results""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Solve the problem using a combinatorial approach:
                - Apply counting principles or generating functions
                - Validate intermediate results""",
                context=analysis
            )
        )

        # Phase 3: Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this solution attempt. Ensure all steps are logically consistent and mathematically rigorous.",
                context=strategy
            ) for strategy in strategies]
        )

        # Phase 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Evaluate the refined solutions:
            - Select the most robust and mathematically sound approach
            - Synthesize insights from multiple strategies if necessary
            - Ensure the final answer is an exact integer between 000 and 999""",
            contexts_list=refined_strategies
        )

        # Phase 5: Final Answer Extraction
        formatted_answer = await self.generate(
            instruction=f"""Extract the final answer from the solution: {final_solution}
            - Ensure the answer is an exact integer between 000 and 999
            - Format the answer appropriately""",
            context=final_solution
        )

        return formatted_answer