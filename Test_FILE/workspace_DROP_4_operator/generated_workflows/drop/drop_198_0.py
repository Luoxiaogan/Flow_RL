# Workflow ID: drop_198_0
# Benchmark: drop
# Data Indices: [200, 17]

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

        # Step 1: Extract Entities and Numbers
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve References
        resolved_entities = await self.revise(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Entities and Numbers: {entities_and_numbers}
            Ensure each reference points to the correct entity.""",
            context=entities_and_numbers
        )

        # Step 3: Classify Problem Type and Identify Operation
        classification = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?
            Provide structured classification.""",
            context=resolved_entities
        )

        # Step 4: Conditional Branching Based on Classification
        if "numerical" in classification.lower() and "exact" in classification.lower():
            # Generate multiple solution attempts in parallel
            solution_attempts = await asyncio.gather(
                self.generate(instruction="Attempt solution using addition...", context=resolved_entities),
                self.generate(instruction="Attempt solution using subtraction...", context=resolved_entities),
                self.generate(instruction="Attempt solution using counting...", context=resolved_entities)
            )
            # Select the best solution
            best_solution = await self.ensemble(
                instruction="Select the most accurate and complete solution.",
                contexts_list=solution_attempts
            )
        elif "estimation" in classification.lower():
            estimates = await asyncio.gather(
                self.generate(instruction="Estimate using order of magnitude...", context=resolved_entities),
                self.generate(instruction="Estimate using dimensional analysis...", context=resolved_entities),
                self.generate(instruction="Estimate using comparable examples...", context=resolved_entities)
            )
            best_solution = await self.ensemble(
                instruction="Synthesize estimates into best approximation",
                contexts_list=estimates
            )
        else:
            # Default comprehensive approach
            best_solution = await self.generate(
                instruction="Apply general problem-solving framework...",
                context=resolved_entities
            )

        # Step 5: Iterative Refinement
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"Validate solution: {best_solution}",
                context=resolved_entities
            )
            if "error" in validation.lower():
                best_solution = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=best_solution
                )
            else:
                break

        # Step 6: Format Final Answer
        final_answer = await self.revise(
            instruction=f"""Format the final answer to match the expected format:
            Classification: {classification}
            Solution: {best_solution}""",
            context=best_solution
        )

        return final_answer