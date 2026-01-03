# Workflow ID: gsm8k_4_0
# Benchmark: gsm8k
# Data Indices: [116, 73]

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

        # Step 1: Initial Analysis - Extract entities and classify problem type
        extraction_task = self.generate(
            instruction="""Extract all numerical values, entities, and relationships:
            - Numbers: [values and what they represent]
            - Entities: [people, objects, or concepts involved]
            - Relationships: [how entities interact or relate]""",
            context=""
        )
        classification_task = self.generate(
            instruction="""Classify the problem type:
            - Sequential operations
            - Rate problems (distance/speed/time, work rates, etc.)
            - Distribution (dividing quantities, equal sharing, remainders)
            - Proportions (percentages, fractions, ratios, scaling)
            - Multi-entity tracking""",
            context=""
        )
        extracted_info, problem_type = await asyncio.gather(extraction_task, classification_task)

        # Step 2: Synthesize initial analysis
        unified_representation = await self.ensemble(
            instruction="Combine extracted information and problem classification into a unified representation.",
            contexts_list=[extracted_info, problem_type]
        )

        # Step 3: Strategy Selection - Branch based on problem type
        if "rate" in problem_type.lower():
            solution_steps = await self.solve_rate_problem(unified_representation)
        elif "distribution" in problem_type.lower():
            solution_steps = await self.solve_distribution_problem(unified_representation)
        else:
            solution_steps = await self.solve_general_problem(unified_representation)

        # Step 4: Final Validation
        final_answer = await self.validate_and_finalize(solution_steps)
        return final_answer

    async def solve_rate_problem(self, context):
        # Identify and apply relevant formulas
        formula_identification = await self.generate(
            instruction="Identify the relevant formulas for this rate problem (e.g., distance = speed × time).",
            context=context
        )
        solution_steps = await self.generate(
            instruction=f"Using the identified formulas: {formula_identification}, solve the problem step-by-step.",
            context=context
        )
        return solution_steps

    async def solve_distribution_problem(self, context):
        # Iterative calculations for dividing quantities
        solution_steps = await self.generate(
            instruction="Divide quantities step-by-step, ensuring clarity and precision in each calculation.",
            context=context
        )
        return solution_steps

    async def solve_general_problem(self, context):
        # General step-by-step solution
        solution_steps = await self.generate(
            instruction="Solve the problem step-by-step, showing all intermediate calculations and reasoning.",
            context=context
        )
        return solution_steps

    async def validate_and_finalize(self, solution_steps):
        # Validate intermediate results and finalize the answer
        validation = await self.revise(
            instruction="Validate all intermediate results and ensure the final answer satisfies the problem's constraints.",
            context=solution_steps
        )
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the validated solution.",
            context=validation
        )
        return final_answer