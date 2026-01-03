# Workflow ID: gsm8k_88_0
# Benchmark: gsm8k
# Data Indices: [226, 63]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify all numbers and their units/contexts
            - List all entities (people, objects, etc.) and their roles
            - Identify relationships and constraints
            - Clearly state what the problem is asking for
            Format the output as a structured summary.""",
            context=""
        )

        # Phase 2: Solution Planning
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a step-by-step plan to solve the problem:
            - Define each calculation step clearly
            - Specify the order of operations
            - Note any dependencies between steps
            - Highlight potential pitfalls or ambiguities""",
            context=analysis
        )

        # Phase 3: Parallel Execution Attempts
        execution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Execute the plan:
                {plan}
                
                Perform all calculations step-by-step, showing intermediate results.
                Ensure each step logically follows from the previous one.""",
                context=plan
            ),
            self.generate(
                instruction=f"""Re-execute the plan with a different approach:
                {plan}
                
                Try alternative methods for calculations if applicable.
                Focus on clarity and precision.""",
                context=plan
            )
        )

        # Phase 4: Validation and Refinement
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this solution:
                {attempt}
                
                Check for:
                - Correctness of calculations
                - Logical consistency
                - Proper handling of units and context""",
                context=attempt
            ) for attempt in execution_attempts]
        )

        # Phase 5: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Choose the most accurate and complete solution
            - Resolve any discrepancies between options
            - Ensure the final answer is clear and precise""",
            contexts_list=validated_solutions
        )

        # Phase 6: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer:
            - Ensure it is a single number (integer or decimal)
            - Remove any extraneous text or explanations""",
            context=final_solution
        )

        return final_answer.strip()