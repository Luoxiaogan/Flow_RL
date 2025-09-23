# Workflow ID: mgsmbn_93_0
# Benchmark: mgsmbn
# Data Indices: [147]

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

        # Step 1: Semantic Decomposition - Extract entities, numbers, relations, and question
        decomposition = await self.generate(
            instruction="""Perform a comprehensive semantic decomposition of the Bengali math problem. Extract:
            1. All named entities (people, objects) and their roles.
            2. All numerical values and what they quantify (e.g., "30 বছর" → age of Jane).
            3. Temporal markers (e.g., "দুই বছর আগে") and their implications.
            4. Comparative or relational phrases (e.g., "থেকে বড়", "অর্ধেক") and their mathematical meaning.
            5. The explicit question being asked (e.g., "জিনের বয়স কত?").
            Format as a structured list with clear labels for each category.""",
            context=""
        )

        # Step 2: Constraint Mapping - Convert relations to mathematical expressions
        constraints = await self.revise(
            instruction="""Transform the extracted relationships into formal mathematical expressions or logical constraints.
            For each entity, define its value or equation. Explicitly state:
            - Which variables are known (with values)
            - Which are unknown (with symbols)
            - Which equations link them
            - Any implicit constraints (e.g., ages must be positive, whole numbers for people)
            Ensure temporal shifts are properly modeled (e.g., "two years ago" → subtract 2 from current age).""",
            context=decomposition
        )

        # Step 3: Problem Classification - Determine solution strategy
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            A. Direct substitution (known values plug directly into formula)
            B. Single-variable algebra (one unknown, solvable by rearrangement)
            C. Multi-variable system (multiple unknowns requiring simultaneous equations)
            D. Temporal sequence (step-by-step changes over time)
            E. Proportional scaling (ratios, percentages, fractions)
            Justify your classification with 1-2 sentences referencing the constraints extracted earlier.""",
            context=constraints
        )

        # Step 4: Strategy Execution (Conditional Branching)
        solution_attempt = None
        
        if "A." in classification or "B." in classification or "D." in classification:
            # Direct or single-variable: solve sequentially
            solution_attempt = await self.generate(
                instruction=f"""Solve the problem using the constraints and classification below.
                Classification: {classification}
                Constraints: {constraints}
                Show all steps clearly. For temporal problems, solve chronologically.
                For algebraic problems, show equation rearrangement.
                Box the final numerical answer at the end.""",
                context=constraints
            )
        elif "C." in classification:
            # Multi-variable: parallel solution attempts
            solution_paths = await asyncio.gather(
                self.generate(instruction=f"Solve by isolating variable 1 first. Constraints: {constraints}", context=constraints),
                self.generate(instruction=f"Solve by isolating variable 2 first. Constraints: {constraints}", context=constraints),
                self.generate(instruction=f"Solve by substitution method. Constraints: {constraints}", context=constraints)
            )
            solution_attempt = await self.ensemble(
                instruction="Select the most consistent and mathematically sound solution. Verify that it satisfies all original constraints.",
                contexts_list=solution_paths
            )
        else:  # E. Proportional scaling
            solution_attempt = await self.generate(
                instruction=f"""Solve using proportional reasoning. Constraints: {constraints}
                Show ratio setups, cross-multiplication, or percentage calculations as needed.
                Verify that the final answer maintains proportional relationships stated in the problem.""",
                context=constraints
            )

        # Step 5: Validation Loop (up to 2 iterations)
        validated_solution = solution_attempt
        for _ in range(2):
            validation = await self.generate(
                instruction=f"""Verify this solution by substituting the answer back into the original problem's conditions.
                Check:
                1. Logical consistency (e.g., no negative ages, fractional people unless allowed)
                2. Unit compatibility (e.g., years match years, rupees match rupees)
                3. Satisfaction of all stated relationships
                If any inconsistency is found, diagnose the error and propose a corrected solution.
                If fully consistent, respond with 'VALID: [answer]'.""",
                context=validated_solution
            )
            if "VALID:" in validation:
                break
            else:
                validated_solution = await self.revise(
                    instruction=f"Fix the solution based on this validation feedback: {validation}",
                    context=validated_solution
                )

        # Step 6: Answer Extraction - Distill to single numerical value
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - If multiple numbers appear, select the one that directly answers the original question.
            - Remove all units, explanations, and punctuation.
            - Return ONLY the number (integer or decimal) as a string.
            Example: If text says "জিনের বয়স 23 বছর", return "23".""",
            context=validated_solution
        )

        # Clean and return final answer
        # Remove any remaining non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer)
        return cleaned_answer