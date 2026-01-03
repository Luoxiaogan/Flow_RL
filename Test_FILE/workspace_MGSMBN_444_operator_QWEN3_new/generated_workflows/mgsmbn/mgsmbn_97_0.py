# Workflow ID: mgsmbn_97_0
# Benchmark: mgsmbn
# Data Indices: [103]

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

        # PHASE 1: PARALLEL SEMANTIC DECOMPOSITION
        # Extract entities, relations, and classify problem type simultaneously
        entity_extraction = self.generate(
            instruction="""Extract all named entities, quantities, and units from the Bengali problem.
            Format as a structured list:
            - Entities: [name: value with unit]
            - Unknowns: [what we need to find]
            - Key verbs: [actions that imply operations: 'বেশি' = more, 'কম' = less, 'গুণ' = times, etc.]
            Focus on numerical relationships and hidden comparisons.""",
            context=""
        )
        
        relation_extraction = self.generate(
            instruction="""Identify all mathematical relationships and constraints:
            - Comparative: X is [more/less] than Y by Z
            - Proportional: X is [fraction/ratio/percentage] of Y
            - Sequential: First A happens, then B
            - Distribution: Total divided among N entities
            Express relationships as equations or inequalities where possible.""",
            context=""
        )
        
        classification = self.generate(
            instruction="""Classify this problem into one primary type:
            1. COMPARISON (involves 'more than', 'less than', differences)
            2. RATE (involves speed, time, work, unit price)
            3. DISTRIBUTION (sharing, dividing, remainders)
            4. PROPORTIONAL (ratios, percentages, scaling)
            5. SEQUENTIAL (multi-step chronological operations)
            Also identify required operations: +, -, ×, ÷, algebra, unit conversion.
            State confidence level (High/Medium/Low).""",
            context=""
        )

        # Gather parallel results
        entity_analysis, relation_analysis, problem_classification = await asyncio.gather(
            entity_extraction, relation_extraction, classification
        )

        # PHASE 2: ENSEMBLE SYNTHESIS - BUILD UNIFIED MATHEMATICAL MODEL
        synthesized_model = await self.ensemble(
            instruction="""Synthesize these three perspectives into a single coherent mathematical model:
            1. Combine entities and relations into a structured representation
            2. Resolve conflicts by prioritizing numerical consistency
            3. Identify the target variable to solve for
            4. Map to the classified problem type
            Output format:
            {
                "entities": {"name": value},
                "relations": ["equation1", "equation2"],
                "target": "variable_to_solve",
                "problem_type": "type_from_classification",
                "required_operations": ["op1", "op2"]
            }
            Be explicit about assumptions made.""",
            contexts_list=[entity_analysis, relation_analysis, problem_classification]
        )

        # PHASE 3: CONDITIONAL STRATEGY SELECTION
        strategy_context = synthesized_model
        
        if "COMPARISON" in synthesized_model or "comparison" in synthesized_model.lower():
            solution = await self.generate(
                instruction=f"""Solve using algebraic substitution:
                Given model: {synthesized_model}
                Steps:
                1. Assign variables to unknowns
                2. Write equations based on relations
                3. Solve system of equations
                4. Substitute known values
                5. Calculate final answer
                Show all steps clearly. Verify that answer satisfies all relations.""",
                context=strategy_context
            )
        elif "RATE" in synthesized_model or "rate" in synthesized_model.lower():
            solution = await self.generate(
                instruction=f"""Solve using dimensional analysis and unit tracking:
                Given model: {synthesized_model}
                Steps:
                1. Identify rate formula (distance = speed × time, etc.)
                2. Ensure all units are consistent
                3. Convert units if necessary
                4. Plug in values and calculate
                5. Verify dimensional consistency
                Show unit conversions explicitly.""",
                context=strategy_context
            )
        elif "DISTRIBUTION" in synthesized_model or "distribution" in synthesized_model.lower():
            solution = await self.generate(
                instruction=f"""Solve using division and remainder tracking:
                Given model: {synthesized_model}
                Steps:
                1. Identify total quantity and number of recipients
                2. Perform division
                3. Track quotient and remainder
                4. Interpret remainder in context (discard? distribute? round?)
                5. Calculate final answer
                Consider real-world constraints (no fractional people/items).""",
                context=strategy_context
            )
        elif "PROPORTIONAL" in synthesized_model or "proportional" in synthesized_model.lower():
            solution = await self.generate(
                instruction=f"""Solve using proportional reasoning:
                Given model: {synthesized_model}
                Steps:
                1. Set up proportion equation
                2. Cross-multiply and solve
                3. Handle percentages as fractions of 100
                4. Scale appropriately
                5. Verify proportion holds
                Show ratio setups clearly.""",
                context=strategy_context
            )
        else:  # Default to sequential arithmetic
            solution = await self.generate(
                instruction=f"""Solve using step-by-step arithmetic:
                Given model: {synthesized_model}
                Steps:
                1. List operations in chronological order
                2. Perform calculations sequentially
                3. Track intermediate results
                4. Combine for final answer
                5. Verify order of operations
                Show each step with reasoning.""",
                context=strategy_context
            )

        # PHASE 4: VALIDATION AND REFINEMENT LOOP (up to 3 iterations)
        refined_solution = solution
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                - Does the answer make sense in real-world context?
                - Are units preserved and consistent?
                - Are there any physical/logical impossibilities?
                - Does it satisfy all original problem constraints?
                - Would a 5th grader find this reasonable?
                If any issues found, describe them specifically. Otherwise, say 'VALID'.""",
                context=refined_solution
            )
            
            if "VALID" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break
            else:
                refined_solution = await self.revise(
                    instruction=f"""Fix the issues identified in validation:
                    Validation feedback: {validation}
                    Original solution: {refined_solution}
                    Preserve correct parts, fix only what's wrong.
                    Maintain step-by-step reasoning.
                    Ensure final answer is numerically sound and contextually plausible.""",
                    context=refined_solution
                )

        # PHASE 5: ANSWER DISTILLATION
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution.
            - If multiple numbers appear, select the one that directly answers the original question
            - Remove units, explanations, and intermediate steps
            - Round to nearest integer unless problem explicitly requires decimals
            - If answer is fractional, convert to decimal (e.g., 1/2 → 0.5)
            - Output ONLY the number, nothing else""",
            context=refined_solution
        )

        return final_answer