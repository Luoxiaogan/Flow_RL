# Workflow ID: mgsmbn_35_0
# Benchmark: mgsmbn
# Data Indices: [192, 115]

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
        import json
        import re

        # PHASE 1: STRUCTURAL DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Perform deep structural decomposition of this Bengali math problem. Extract:
            1. ENTITIES: All named objects/people (e.g., students, bees, doors A/B/C, queen bees)
            2. INITIAL QUANTITIES: Starting numbers with units (e.g., "1000 students", "700 bees")
            3. TRANSFORMATION RULES: Operations, fractions, percentages, ratios (e.g., "30% leave", "twice as many")
            4. TARGET QUERY: What is being asked? (e.g., "students exiting door C", "number of worker bees")
            5. CONSTRAINTS: Implicit limits (e.g., "must be integer", "sum must equal initial")
            Format as JSON with keys: entities, initial_quantities, transformations, target, constraints""",
            context=""
        )

        # PHASE 2: STRATEGY CLASSIFICATION & PARALLEL SOLVING
        strategy_analysis = await self.generate(
            instruction=f"""Based on decomposition:
            {decomposition}
            
            Classify problem type and generate 3 distinct solution strategies:
            STRATEGY 1: Algebraic Modeling (define variables, set up equations)
            STRATEGY 2: Step-by-Step Arithmetic (sequential calculation with intermediate values)
            STRATEGY 3: Proportional Reasoning (ratios, scaling, unit analysis)
            For each, specify: approach, key steps, potential pitfalls. Output as numbered list.""",
            context=decomposition
        )

        # PARALLEL EXECUTION OF STRATEGIES
        strategy_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
                Problem decomposition: {decomposition}
                Strategy: {strategy_analysis.split('STRATEGY 1:')[1].split('STRATEGY 2:')[0] if 'STRATEGY 1:' in strategy_analysis else strategy_analysis}
                Steps:
                1. Define variables for unknowns
                2. Translate Bengali relationships into equations
                3. Solve system step by step
                4. Box final answer as ### <number> ###
                Show all work. Verify solution satisfies original constraints.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using STEP-BY-STEP ARITHMETIC:
                Problem decomposition: {decomposition}
                Strategy: {strategy_analysis.split('STRATEGY 2:')[1].split('STRATEGY 3:')[0] if 'STRATEGY 2:' in strategy_analysis else strategy_analysis}
                Steps:
                1. Start with initial quantities
                2. Apply each transformation sequentially
                3. Track intermediate results with units
                4. Box final answer as ### <number> ###
                Show calculations. Verify no step violates constraints.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using PROPORTIONAL REASONING:
                Problem decomposition: {decomposition}
                Strategy: {strategy_analysis.split('STRATEGY 3:')[1] if 'STRATEGY 3:' in strategy_analysis else strategy_analysis}
                Steps:
                1. Identify base quantities and scaling factors
                2. Set up proportions/ratios
                3. Cross-multiply or scale appropriately
                4. Box final answer as ### <number> ###
                Justify proportionality. Check unit consistency.""",
                context=decomposition
            )
        )

        # PHASE 3: VALIDATION & REVISION
        validated_solutions = []
        for i, solution in enumerate(strategy_solutions):
            validation = await self.generate(
                instruction=f"""CRITICALLY VALIDATE this solution:
                Original decomposition: {decomposition}
                Solution attempt: {solution}
                Check:
                1. Arithmetic accuracy (recalculate key steps)
                2. Semantic alignment (does math match Bengali description?)
                3. Constraint satisfaction (e.g., integer counts, sum consistency)
                4. Unit handling
                If errors found, explain precisely. If valid, output "VALID: ### <number> ###".""",
                context=solution
            )
            
            if "VALID:" in validation:
                validated_solutions.append(validation)
            else:
                # REVISE IF INVALID
                revised = await self.revise(
                    instruction=f"""FIX ERRORS identified in validation:
                    Validation feedback: {validation}
                    Original solution: {solution}
                    Problem decomposition: {decomposition}
                    Correct all errors while preserving correct parts. 
                    Output revised solution with boxed answer ### <number> ###""",
                    context=solution
                )
                # RE-VALIDATE REVISED SOLUTION
                revalidation = await self.generate(
                    instruction=f"""FINAL VALIDATION:
                    Revised solution: {revised}
                    Original decomposition: {decomposition}
                    If fully correct, output "VALID: ### <number> ###". Otherwise, output error.""",
                    context=revised
                )
                validated_solutions.append(revalidation if "VALID:" in revalidation else revised)

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_answer = await self.ensemble(
            instruction="""SELECT BEST ANSWER from validated solutions:
            Criteria:
            1. Mathematical correctness (priority #1)
            2. Alignment with problem semantics
            3. Clarity of reasoning
            4. Consistency across strategies
            Extract the numerical answer from the most reliable solution. 
            If multiple valid answers, choose the one with strongest justification.
            Output ONLY the number (integer or decimal) - no text.""",
            contexts_list=validated_solutions
        )

        # PHASE 5: SANITY CHECK & OUTPUT
        sanity_check = await self.generate(
            instruction=f"""FINAL SANITY CHECK:
            Proposed answer: {final_answer}
            Problem decomposition: {decomposition}
            Verify:
            1. Answer is positive and realistic (e.g., no negative people)
            2. Matches expected magnitude (e.g., not larger than initial quantity)
            3. Satisfies all constraints from decomposition
            If passes, output ### {final_answer} ###. If fails, output "ERROR".""",
            context=final_answer
        )

        # EXTRACT NUMERICAL ANSWER
        match = re.search(r'###\s*([\d.]+)\s*###', sanity_check)
        if match:
            return match.group(1)
        else:
            # FALLBACK: Return ensemble answer if sanity check malformed
            return final_answer.strip()