# Workflow ID: mgsmbn_17_0
# Benchmark: mgsmbn
# Data Indices: [191]

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

        # PHASE 1: PARALLEL EXTRACTION - Build multi-perspective problem model
        entity_extraction = await self.generate(
            instruction="""Extract a comprehensive structured model of the problem. Include:
            1. ENTITIES: List every person, object, or quantity mentioned. For each, specify:
               - Name/identifier
               - Known attributes (age, price, count, etc.)
               - Unknown attributes (what needs to be found)
            2. RELATIONSHIPS: For every pair of entities, specify:
               - Mathematical relationship (e.g., "A is twice B", "C = D + 5")
               - Temporal/logical sequence (e.g., "first X happened, then Y")
               - Comparative relationships (e.g., "older than", "more expensive")
            3. CONSTRAINTS: List all explicit and implicit constraints:
               - Unit constraints (e.g., "must be integer", "in টাকা")
               - Physical constraints (e.g., "can't be negative", "must be whole person")
               - Contextual constraints (e.g., "school problem implies reasonable numbers")
            4. TARGET: Clearly state what the question is asking for.
            Format as a structured markdown table for each section. Resolve pronouns. Flag any ambiguities.""",
            context=""
        )

        # PHASE 2: CONDITIONAL BRANCHING - Assess model quality
        model_assessment = await self.generate(
            instruction=f"""Assess the quality and completeness of this problem model:
            {entity_extraction}

            Evaluate:
            1. Are all entities clearly identified with no ambiguous pronouns?
            2. Are all relationships mathematically precise and unambiguous?
            3. Are constraints comprehensive and contextually appropriate?
            4. Is the target variable clearly defined?

            Classify as:
            - "CLEAN": All elements are clear, complete, and unambiguous
            - "AMBIGUOUS": Some relationships or entities need clarification
            - "INCOMPLETE": Missing critical constraints or relationships

            Also, estimate confidence level (0-100%) in model accuracy.
            Output ONLY the classification and confidence as: "CLASSIFICATION: [label], CONFIDENCE: [number]" """,
            context=entity_extraction
        )

        # If model is ambiguous or incomplete, trigger refinement
        if "AMBIGUOUS" in model_assessment or "INCOMPLETE" in model_assessment:
            refined_model = await self.revise(
                instruction=f"""Refine the problem model to resolve ambiguities and fill gaps. 
                Original assessment: {model_assessment}
                
                Focus areas:
                1. Disambiguate pronouns and vague references
                2. Make implicit relationships explicit (e.g., "twice as much" → "A = 2×B")
                3. Add missing constraints based on real-world context
                4. Verify chronological/logical sequencing is complete
                5. Ensure target variable is precisely defined

                Output the complete refined model in the same structured format as before.""",
                context=entity_extraction
            )
            working_model = refined_model
        else:
            working_model = entity_extraction

        # PHASE 3: PARALLEL SOLUTION GENERATION - Try multiple approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using DIRECT ARITHMETIC approach:
                Problem Model: {working_model}

                Steps:
                1. Identify starting values and sequence of operations
                2. Perform calculations step by step, showing intermediate results
                3. Track units throughout
                4. Verify each step against constraints
                5. Box final answer

                Show ALL work. Be meticulous about order of operations.""",
                context=working_model
            ),
            self.generate(
                instruction=f"""Solve using ALGEBRAIC FORMULATION approach:
                Problem Model: {working_model}

                Steps:
                1. Assign variables to unknowns
                2. Write equations based on relationships
                3. Solve system of equations step by step
                4. Substitute known values
                5. Verify solution satisfies all constraints
                6. Box final answer

                Show ALL algebraic manipulations. Check for extraneous solutions.""",
                context=working_model
            ),
            self.generate(
                instruction=f"""Solve using UNIT TRACKING & PROPORTIONAL REASONING approach:
                Problem Model: {working_model}

                Steps:
                1. Identify base units and conversion factors
                2. Set up proportions or unit chains
                3. Cancel units systematically
                4. Calculate final value with unit consistency
                5. Verify answer makes sense in context
                6. Box final answer

                Show unit cancellation visually. Check dimensional consistency.""",
                context=working_model
            )
        )

        # PHASE 4: ENSEMBLE SYNTHESIS - Combine and validate solutions
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution attempts into one definitive answer. Process:
            1. Compare all three solutions. Do they agree numerically?
            2. If they agree, select the most clearly reasoned one.
            3. If they disagree, identify which one(s) violate constraints or make logical errors.
            4. Cross-validate intermediate steps against the problem model.
            5. Check for unit consistency and real-world plausibility.
            6. If still uncertain, choose the solution with the most rigorous step-by-step justification.
            7. Output the final answer in this exact format: "FINAL ANSWER: [number]" """,
            contexts_list=solution_attempts
        )

        # PHASE 5: FINAL VALIDATION & EXTRACTION
        validated_answer = await self.revise(
            instruction=f"""Extract and validate the final numerical answer:
            Synthesized Solution: {synthesized_solution}
            Problem Model: {working_model}

            Steps:
            1. Extract the numerical value from "FINAL ANSWER: [number]"
            2. Verify it satisfies all constraints from the problem model
            3. Check if decimal places are appropriate (e.g., money might need 2 decimals, people must be integer)
            4. If validation fails, correct the answer to meet constraints (e.g., round to nearest integer if required)
            5. Output ONLY the final numerical value, nothing else.

            Example outputs: "68", "15.5", "3" """,
            context=synthesized_solution
        )

        # Clean extraction (in case revision output has extra text)
        final_answer = await self.generate(
            instruction=f"""From the following text, extract ONLY the final numerical answer. 
            Remove any units, labels, or explanatory text. If multiple numbers exist, 
            choose the one that directly answers the original question.
            Text: {validated_answer}
            Output ONLY the number, as a string.""",
            context=validated_answer
        )

        # Final cleanup - ensure it's a clean number string
        clean_answer = re.sub(r'[^\d\.]', '', final_answer.strip())
        return clean_answer