# Workflow ID: gsm8k_93_0
# Benchmark: gsm8k
# Data Indices: [185, 36]

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

        # Step 1: Extract problem structure (parallel fork)
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: [names, objects, and roles]
            - Numbers: [values and what they represent]
            - Relationships: [how entities and numbers are connected]""",
            context=""
        )
        constraints = await self.generate(
            instruction="""Identify all constraints and conditions:
            - Explicit constraints stated in the problem
            - Implicit constraints from context
            - Physical or logical limitations""",
            context=entities
        )

        # Combine extracted information into a unified context
        problem_structure = f"{entities}\n{constraints}"

        # Step 2: Classify problem type (conditional branching)
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            1. Sequential Operations
            2. Rate Problems (distance/speed/time, work rates, unit prices)
            3. Distribution (dividing quantities, equal sharing, remainders)
            4. Proportions (percentages, fractions, ratios, scaling)
            5. Multi-entity (tracking different quantities for multiple people/objects)""",
            context=problem_structure
        )

        # Define solution strategy based on classification
        if "rate" in classification.lower():
            solution_strategy = "Use rate formulas (e.g., distance = speed × time). Convert units if necessary."
        elif "distribution" in classification.lower():
            solution_strategy = "Divide quantities equally or proportionally. Handle remainders if applicable."
        elif "proportions" in classification.lower():
            solution_strategy = "Apply scaling factors or convert percentages/fractions to decimals."
        else:
            solution_strategy = "Follow a step-by-step calculation chain."

        # Step 3: Generate solution steps (sequential chain)
        solution_steps = await self.generate(
            instruction=f"""Using the problem structure and classification:
            Problem Structure: {problem_structure}
            Classification: {classification}
            Solution Strategy: {solution_strategy}
            
            Generate a step-by-step solution plan with intermediate results.""",
            context=problem_structure
        )

        # Step 4: Validate and refine intermediate results (iterative loop)
        refined_steps = solution_steps
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.revise(
                instruction="Check for errors in calculations or logical inconsistencies.",
                context=refined_steps
            )
            if "error" not in validation.lower():
                break
            refined_steps = await self.revise(
                instruction=f"Fix issues identified in validation: {validation}",
                context=refined_steps
            )

        # Step 5: Summarize final result
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the refined solution steps.",
            context=refined_steps
        )

        return final_answer.strip()