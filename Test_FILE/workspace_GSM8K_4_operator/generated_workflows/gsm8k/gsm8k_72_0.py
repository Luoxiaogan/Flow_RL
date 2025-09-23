# Workflow ID: gsm8k_72_0
# Benchmark: gsm8k
# Data Indices: [88, 290]

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
        import re

        # Step 1: Hierarchical Decomposition
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - Numbers: [values and what they represent]
            - Units: [units associated with numbers]
            - Relationships: [how entities interact]""",
            context=""
        )

        constraints = await self.generate(
            instruction=f"""Identify all constraints and conditions:
            - Explicit constraints stated in problem
            - Implicit constraints from context
            - Physical or logical limitations
            - Boundary conditions""",
            context=entities
        )

        goal = await self.generate(
            instruction=f"""Clarify the goal:
            - What is being asked for?
            - What format should the answer take?""",
            context=f"{entities}\n{constraints}"
        )

        # Step 2: Parallel Solution Attempts
        direct_calc = self.generate(
            instruction=f"""Solve using direct calculation:
            - Perform step-by-step arithmetic
            - Show intermediate results
            - Ensure units are consistent""",
            context=f"{entities}\n{constraints}\n{goal}"
        )

        unit_analysis = self.generate(
            instruction=f"""Validate using unit analysis:
            - Check unit consistency
            - Identify conversion factors if needed""",
            context=f"{entities}\n{constraints}\n{goal}"
        )

        logical_validation = self.generate(
            instruction=f"""Validate using logical reasoning:
            - Does the solution make sense in context?
            - Are there any contradictions?""",
            context=f"{entities}\n{constraints}\n{goal}"
        )

        attempts = await asyncio.gather(direct_calc, unit_analysis, logical_validation)

        # Step 3: Synthesize Solutions
        synthesis = await self.ensemble(
            instruction="""Synthesize multiple perspectives:
            - Combine insights from direct calculation, unit analysis, and logical validation
            - Resolve conflicts between approaches
            - Produce a unified solution""",
            contexts_list=attempts
        )

        # Step 4: Iterative Refinement
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.revise(
                instruction=f"""Validate the solution:
                - Check against constraints
                - Identify errors or gaps
                - Suggest corrections""",
                context=synthesis
            )

            if "error" not in validation.lower():
                break

            synthesis = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                - Address identified issues
                - Update intermediate results
                - Ensure final answer is accurate""",
                context=f"{synthesis}\n{validation}"
            )

        # Step 5: Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer:
            - Ensure it matches the goal format
            - Remove any extraneous text""",
            context=synthesis
        )

        # Clean up final answer to extract only the numerical value
        match = re.search(r"[-+]?\d*\.\d+|\d+", final_answer)
        return float(match.group()) if match else None