# Workflow ID: high_level_math_ganluo_28_0
# Benchmark: high_level_math_ganluo
# Data Indices: [3]

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

        # Step 1: Extract key information (equation, variable constraints, etc.)
        extraction = await self.generate(
            instruction="Extract the mathematical equation, variable constraints, and any other relevant details from the problem. "
                       "Ensure the output includes the equation in a simplified form and the range of possible values for each variable.",
            context=self.problem_text
        )

        # Step 2: Reformulate the problem for solution generation
        reformulation = await self.generate(
            instruction=f"Based on the extracted information: {extraction}, "
                       "reformulate the problem into a structured format suitable for generating candidate solutions. "
                       "Include instructions for isolating variables or simplifying the equation if necessary.",
            context=self.problem_text
        )

        # Step 3: Generate candidate solutions
        candidates = await self.generate(
            instruction=f"Using the reformulated problem: {reformulation}, "
                       "generate all possible candidate solutions by systematically exploring the range of values for each variable. "
                       "Ensure all constraints are satisfied and include edge cases in the exploration.",
            context=self.problem_text
        )

        # Step 4: Validate and refine solutions
        validation = await self.revise(
            instruction="Validate the candidate solutions against the original equation and constraints. "
                       "Eliminate any invalid solutions and ensure the remaining solutions are mathematically correct.",
            context=candidates
        )

        # Step 5: Summarize results
        summary = await self.summarize(
            instruction="Condense the validated solutions into a concise format. "
                       "Provide the total count of valid ordered pairs and any other relevant summary information.",
            context=validation
        )

        return summary