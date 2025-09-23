# Workflow ID: mgsmbn_66_0
# Benchmark: mgsmbn
# Data Indices: [88]

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

        # STEP 1: SEMANTIC DECOMPOSITION - Extract narrative structure, entities, quantities, units, relationships
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali word problem. Identify:
            1. All actors (people, objects, entities involved)
            2. All actions (what happens, in chronological order)
            3. All numerical values with their units (টাকা, লিটার, ফুট, সেকেন্ড, etc.) and what they represent
            4. All relationships (ratios, rates, proportions, dependencies)
            5. The explicit question being asked (what is unknown?)
            6. Any constraints or conditions (time limits, physical limits, logical boundaries)
            7. Implicit assumptions (e.g., constant speed, no loss, equal distribution)

            Format your output as a structured report with clear section headers. Be exhaustive. Do not solve yet—only model the scenario.
            Example format:
            ACTORS: [list]
            ACTIONS: [chronological list with associated quantities]
            QUANTITIES: [value + unit + description]
            RELATIONSHIPS: [mathematical or logical dependencies]
            UNKNOWN: [what needs to be calculated]
            CONSTRAINTS: [explicit and implicit limits]
            """,
            context=""
        )

        # STEP 2: PROBLEM CLASSIFICATION - Determine problem type to guide solution strategy
        classification = await self.generate(
            instruction=f"""Based on the following decomposition:
            {decomposition}

            Classify this problem into one primary type and up to two secondary types from:
            - Rate/Speed/Time (involves ratios like distance/time, work/time)
            - Distribution/Division (sharing, splitting, remainders)
            - Sequential Operations (multiple steps: deposit then withdraw, buy then sell)
            - Proportional Reasoning (percentages, fractions, scaling)
            - Comparison/Difference (how many more, less, difference between)
            - Multi-entity Tracking (multiple people/objects with different quantities)

            Also assess:
            - Does it require unit conversion?
            - Are there hidden steps or implicit calculations?
            - Is the solution path linear or does it require backward calculation?
            - What is the expected answer format (integer, decimal, rounded)?

            Output a classification report with justification. This will determine the solution strategy.""",
            context=decomposition
        )

        # STEP 3: PARALLEL MODELING - Two independent approaches to build mathematical model
        explicit_model_task = self.generate(
            instruction=f"""Based on decomposition and classification:
            Decomposition: {decomposition}
            Classification: {classification}

            Build a mathematical model using ONLY explicitly stated values and relationships.
            - Translate narrative into equations or step-by-step arithmetic
            - Use variables for unknowns
            - Show unit tracking at each step
            - Do not infer anything not directly stated
            - Output as numbered steps with units preserved""",
            context=decomposition
        )

        implicit_model_task = self.generate(
            instruction=f"""Based on decomposition and classification:
            Decomposition: {decomposition}
            Classification: {classification}

            Build a mathematical model by INFERRING implicit relationships and physical/logical constraints.
            - What rates can be derived? (e.g., speed from distance/time)
            - What assumptions are reasonable? (constant rate, no loss, etc.)
            - What real-world constraints apply? (non-negative quantities, integer people, etc.)
            - How can hidden steps be uncovered? (e.g., total = sum of parts)
            - Output as numbered steps with justifications for each inference""",
            context=decomposition
        )

        # Run both modeling tasks in parallel
        explicit_model, implicit_model = await asyncio.gather(
            explicit_model_task, implicit_model_task
        )

        # STEP 4: ENSEMBLE - Synthesize explicit and implicit models into coherent solution path
        synthesized_model = await self.ensemble(
            instruction="""You have two mathematical models for the same problem:
            1. EXPLICIT MODEL: Based only on directly stated values and relationships.
            2. IMPLICIT MODEL: Based on inferred relationships and real-world constraints.

            Your task:
            - Identify where the models agree and where they conflict.
            - Resolve conflicts by prioritizing physical/logical consistency over literal interpretation.
            - Synthesize a single, coherent, step-by-step solution path that combines the best of both.
            - Ensure unit consistency throughout.
            - Flag any remaining uncertainties or assumptions.
            - Output as a clear, numbered sequence of mathematical operations leading to the answer.""",
            contexts_list=[explicit_model, implicit_model]
        )

        # STEP 5: INITIAL SOLUTION GENERATION
        candidate_solution = await self.generate(
            instruction=f"""Using the synthesized model:
            {synthesized_model}

            Calculate the final numerical answer. Show all steps:
            - Write each calculation explicitly
            - Track units at every step
            - Simplify fractions or decimals as appropriate
            - Box the final answer at the end

            IMPORTANT: Output ONLY the final numerical value at the very end, prefixed by "FINAL_ANSWER: ".
            Example: FINAL_ANSWER: 16""",
            context=synthesized_model
        )

        # STEP 6: VERIFICATION & REFINEMENT LOOP (max 2 iterations)
        current_solution = candidate_solution
        for iteration in range(2):
            verification = await self.revise(
                instruction=f"""VERIFY this solution:
                {current_solution}

                Check:
                1. Unit consistency: Do units cancel correctly? Is final unit appropriate?
                2. Reverse calculation: Can you start from the answer and reconstruct the problem?
                3. Sanity check: Does the answer make sense in context? (e.g., no negative water, no fractional people)
                4. Arithmetic accuracy: Recalculate key steps.
                5. Completeness: Are all given values used? Are any constraints violated?

                If any issue is found, explain it clearly. If no issues, output "VERIFIED: OK".
                If issues exist, suggest specific corrections.""",
                context=current_solution
            )

            if "VERIFIED: OK" in verification or "verified" in verification.lower() or "no issue" in verification.lower():
                break
            else:
                # Revise solution based on verification feedback
                current_solution = await self.revise(
                    instruction=f"""REVISE the solution based on verification feedback:
                    Feedback: {verification}

                    Original solution attempt:
                    {current_solution}

                    Correct errors, improve clarity, ensure unit consistency, and recalculate.
                    Output revised solution with FINAL_ANSWER: prefix at the end.""",
                    context=current_solution
                )

        # STEP 7: EXTRACT FINAL NUMERICAL ANSWER
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below.
            The answer is prefixed by "FINAL_ANSWER: " and is a single number (integer or decimal).
            Strip all units, explanations, and text. Return only the number.
            If multiple numbers appear, return the one immediately following "FINAL_ANSWER: ".
            If no such pattern exists, return the last numerical value in the text.""",
            context=current_solution
        )

        # Clean and return final answer
        # Extract number using regex to handle any residual text
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return raw if no number found (shouldn't happen)
            return final_answer.strip()