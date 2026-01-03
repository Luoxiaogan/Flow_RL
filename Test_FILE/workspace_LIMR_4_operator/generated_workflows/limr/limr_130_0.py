# Workflow ID: limr_130_0
# Benchmark: limr
# Data Indices: [292, 80]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it:
            - Identify known values, unknowns, and constraints.
            - Determine the problem type (e.g., number theory, combinatorics).
            - List applicable mathematical techniques.
            Provide a structured breakdown.""",
            context=""
        )
        
        perspectives = await asyncio.gather(
            self.generate(instruction="Explore algebraic approaches.", context=analysis),
            self.generate(instruction="Explore geometric interpretations.", context=analysis),
            self.generate(instruction="Explore combinatorial strategies.", context=analysis)
        )
        
        summarized_perspectives = await asyncio.gather(
            *[self.summarize(instruction="Condense key insights.", context=p) for p in perspectives]
        )

        # Phase 2: Solution Generation and Validation
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=f"Develop a solution based on: {p}", context="") for p in summarized_perspectives]
        )
        
        validated_solutions = await asyncio.gather(
            *[self.revise(instruction="Verify logical consistency and mathematical accuracy.", context=s) for s in solution_attempts]
        )

        # Phase 3: Synthesis and Selection
        final_solution = await self.ensemble(
            instruction="Select the most robust and accurate solution.",
            contexts_list=validated_solutions
        )
        
        refined_solution = await self.revise(
            instruction="Polish the selected solution for clarity and precision.",
            context=final_solution
        )

        # Phase 4: Output Preparation and Verification
        answer = await self.generate(
            instruction="Extract the final answer (integer between 000 and 999).",
            context=refined_solution
        )
        
        verification = await self.revise(
            instruction="Ensure the answer satisfies all constraints and matches the expected format.",
            context=answer
        )

        return verification