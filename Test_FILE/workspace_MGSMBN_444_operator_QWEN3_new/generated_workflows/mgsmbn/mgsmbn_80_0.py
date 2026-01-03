# Workflow ID: mgsmbn_80_0
# Benchmark: mgsmbn
# Data Indices: [19]

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

        # PHASE 1: SEMANTIC DECOMPOSITION — Extract structured understanding
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali word problem. Identify:
            1. All entities (people, objects, places) and their roles
            2. All numerical values with their units and what they quantify
            3. All mathematical relationships (ratios, sums, differences, products, quotients)
            4. The explicit or implicit unknown being asked for
            5. Any constraints or conditions (e.g., "equally divided", "remaining", "total")
            6. Temporal or causal sequence if applicable
            Format as a structured JSON-like outline with clear section headers.
            Pay special attention to Bengali postpositions and contextual pronouns that imply relationships.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION STRATEGIES — Explore multiple mathematical lenses
        algebraic_approach = self.generate(
            instruction=f"""Using the decomposition:
            {decomposition}

            Solve as an algebraic equation:
            - Define variables for unknowns
            - Write governing equations with units
            - Show substitution and simplification steps
            - Solve for the target variable
            - Verify dimensional consistency at each step""",
            context=decomposition
        )

        sequential_approach = self.generate(
            instruction=f"""Using the decomposition:
            {decomposition}

            Solve as a sequence of transactions or steps:
            - Model chronologically if time-based
            - Track cumulative state after each operation
            - Show intermediate totals with units
            - Arrive at final value through stepwise computation""",
            context=decomposition
        )

        constraint_approach = self.generate(
            instruction=f"""Using the decomposition:
            {decomposition}

            Solve as a constraint satisfaction problem:
            - List all explicit and implicit constraints
            - Formulate inequalities or equalities
            - Use logical deduction or substitution
            - Show how constraints narrow down to the solution""",
            context=decomposition
        )

        # Run all three in parallel
        algebraic_result, sequential_result, constraint_result = await asyncio.gather(
            algebraic_approach, sequential_approach, constraint_approach
        )

        # PHASE 3: ENSEMBLE SYNTHESIS — Compare, critique, select best
        final_answer_draft = await self.ensemble(
            instruction="""You are given three solution attempts for the same Bengali math problem.
            Evaluate each on:
            - Mathematical correctness (arithmetic, algebra)
            - Unit consistency throughout
            - Adherence to problem constraints
            - Plausibility of final answer (no negative people, fractional pizzas unless specified)
            - Clarity of reasoning

            Select the most robust solution. If two agree and one differs, explain why the outlier is incorrect.
            If all differ, synthesize a new answer by combining correct elements.
            Output the selected/synthesized solution with a brief justification.""",
            contexts_list=[algebraic_result, sequential_result, constraint_result]
        )

        # PHASE 4: REALITY CHECK — Validate against real-world plausibility
        validated_answer = await self.revise(
            instruction="""Critically validate this answer:
            - Does it make real-world sense? (e.g., no 2.7 people, no negative money spent)
            - Are units preserved and appropriate?
            - Does it satisfy all constraints from the original problem?
            - Is the magnitude reasonable? (e.g., if buying groceries with $50, answer shouldn't be 1000 pizzas)

            If any issue is found, adjust the answer to the nearest plausible value and explain why.
            If no issues, return the answer unchanged with 'VALIDATED' prefix.""",
            context=final_answer_draft
        )

        # PHASE 5: EXTRACTION — Output clean numerical answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - If decimal, preserve necessary precision (max 2 decimal places unless specified)
            - If fractional, convert to decimal
            - Remove all units, explanations, and text
            - Return ONLY the number, nothing else
            - If multiple numbers, return the one that answers the problem's question""",
            context=validated_answer
        )

        # Clean and return
        # Remove any non-numeric characters except decimal point
        clean_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        # Ensure it's a valid number
        try:
            float(clean_answer)
            return clean_answer
        except:
            # Fallback: return first number found in validated answer
            numbers = re.findall(r'\d+\.?\d*', validated_answer)
            return numbers[0] if numbers else "0"