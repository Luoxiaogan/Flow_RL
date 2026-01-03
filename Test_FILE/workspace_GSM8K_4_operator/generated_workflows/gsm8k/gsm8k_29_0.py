# Workflow ID: gsm8k_29_0
# Benchmark: gsm8k
# Data Indices: [126, 205]

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

        # Initial Extraction and Classification
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, relationships, and constraints:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Classify the problem type:
            - Numerical, logical, or textual?
            - Exact calculation or estimation?
            - Multiple valid approaches?
            - Expected answer format?""",
            context=""
        )

        refined_analysis = await self.revise(
            instruction="Refine the extracted information, ensuring completeness and accuracy.",
            context=initial_analysis
        )

        # Solution Path Exploration
        numerical_solution = self.generate(
            instruction=f"""Develop precise mathematical calculations:
            - Show all algebraic steps
            - Maintain full precision
            - Double-check arithmetic
            - Present final answer with appropriate units
            
            Context: {refined_analysis}""",
            context=""
        )

        estimation_solution = self.generate(
            instruction=f"""Develop order-of-magnitude estimates:
            - Use dimensional analysis
            - Use comparable examples
            - Present approximate answer with reasoning
            
            Context: {refined_analysis}""",
            context=""
        )

        solutions = await asyncio.gather(numerical_solution, estimation_solution)

        # Intermediate Results Tracking
        intermediate_results = await asyncio.gather(
            *[self.generate(
                instruction=f"Create structured record of intermediate results for solution: {solution}",
                context=""
            ) for solution in solutions]
        )

        validated_results = await asyncio.gather(
            *[self.revise(
                instruction="Validate each step, correcting errors and ensuring clarity.",
                context=result
            ) for result in intermediate_results]
        )

        # Final Synthesis and Validation
        final_solution = await self.ensemble(
            instruction="Compare and synthesize the best solution from multiple paths.",
            contexts_list=validated_results
        )

        final_answer = await self.summarize(
            instruction="Condense the final solution into a single numerical answer, ensuring it matches the expected format.",
            context=final_solution
        )

        return final_answer