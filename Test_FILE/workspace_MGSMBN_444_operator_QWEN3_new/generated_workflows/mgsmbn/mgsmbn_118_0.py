# Workflow ID: mgsmbn_118_0
# Benchmark: mgsmbn
# Data Indices: [26]

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

        # === PHASE 1: SEMANTIC DECOMPOSITION ===
        entity_extraction = await self.generate(
            instruction="""Thoroughly decompose the Bengali word problem into structured components. Extract and categorize:
            1. ENTITIES: All named persons, objects, or groups (e.g., "অ্যারন", "সিওভান", "রেমন্ড", "রত্ন")
            2. QUANTITIES: All numerical values with their associated entities and units (e.g., "40টি রত্ন" → value=40, unit="রত্ন", owner="রেমন্ড")
            3. RELATIONSHIPS: All comparative, proportional, or sequential relationships (e.g., "2টি কম" → difference=-2, "অর্ধেকের থেকে 5টি বেশি" → formula=half + 5)
            4. TARGET: What is explicitly asked for? (e.g., "সিওভানের কাছে কটি রত্ন?")
            Format output as a structured markdown list with clear section headers. Do not solve yet — only extract and categorize.""",
            context=""
        )

        # === PHASE 2: PROBLEM TYPING & STRATEGY SELECTION ===
        problem_type = await self.generate(
            instruction=f"""Based on the extracted structure:
            {entity_extraction}

            Classify this problem into exactly one primary type:
            - COMPARISON: Involves direct or indirect comparisons (more/less than, difference)
            - PROPORTIONAL: Involves fractions, percentages, ratios, or scaling
            - SEQUENTIAL: Involves ordered steps or state changes over time
            - DISTRIBUTION: Involves dividing, sharing, or allocating quantities
            - MULTI-ENTITY: Involves tracking interdependent quantities across multiple entities

            Then, generate a tailored solution strategy for this type. Include:
            - Key variables to define
            - Order of operations
            - Potential pitfalls specific to this problem
            - Validation checks to perform later
            Output format: "TYPE: [type] | STRATEGY: [detailed strategy]".""",
            context=entity_extraction
        )

        # === PHASE 3: PARALLEL SOLUTION DRAFTING ===
        # Generate 3 independent solution approaches in parallel
        algebraic_draft, arithmetic_draft, contextual_draft = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using ALGEBRAIC modeling:
                Problem Type: {problem_type}
                Extracted Structure: {entity_extraction}

                Steps:
                1. Assign variables to unknowns (e.g., let x = Siobhan's gems)
                2. Translate relationships into equations
                3. Solve system step by step
                4. Box final answer as: \\boxed{{number}}
                Show all work. Prioritize symbolic manipulation over arithmetic.""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using ARITHMETIC step-by-step calculation:
                Problem Type: {problem_type}
                Extracted Structure: {entity_extraction}

                Steps:
                1. Start from known values
                2. Apply operations in logical sequence
                3. Track intermediate results with units
                4. Box final answer as: \\boxed{{number}}
                Show all work. Prioritize numerical computation over variables.""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using CONTEXTUAL real-world reasoning:
                Problem Type: {problem_type}
                Extracted Structure: {entity_extraction}

                Steps:
                1. Interpret problem in real-world terms
                2. Apply common sense constraints (no negative gems, whole persons)
                3. Use estimation or substitution to verify plausibility
                4. Box final answer as: \\boxed{{number}}
                Show all work. Prioritize practical plausibility over formalism.""",
                context=""
            )
        )

        draft_solutions = [algebraic_draft, arithmetic_draft, contextual_draft]

        # === PHASE 4: CROSS-VALIDATION & REVISION LOOP ===
        validated_solutions = []
        for i, draft in enumerate(draft_solutions):
            validation = await self.generate(
                instruction=f"""CRITICALLY VALIDATE this solution draft:
                {draft}

                Check for:
                1. Arithmetic accuracy: Recompute key steps
                2. Unit consistency: Are units preserved and appropriate?
                3. Logical plausibility: Does answer make real-world sense?
                4. Entity alignment: Does answer match the asked entity?
                5. Completeness: Are all relationships from extraction used?

                If errors found, list them specifically. If valid, state "VALID".
                Output format: "STATUS: [VALID/INVALID] | ERRORS: [list or 'none']".""",
                context=draft
            )

            if "INVALID" in validation:
                revised = await self.revise(
                    instruction=f"""REVISE based on validation feedback:
                    Validation: {validation}
                    Original Draft: {draft}

                    Requirements:
                    - Fix all identified errors
                    - Preserve correct parts
                    - Maintain step-by-step reasoning
                    - Box final answer as: \\boxed{{number}}
                    Output only the revised solution.""",
                    context=draft
                )
                validated_solutions.append(revised)
            else:
                validated_solutions.append(draft)

        # === PHASE 5: CONSENSUS SYNTHESIS & ANSWER EXTRACTION ===
        final_synthesis = await self.ensemble(
            instruction="""Synthesize the most reliable answer from these validated solutions:
            - If all agree, output that answer
            - If conflict, identify consistent components and recompute
            - Prioritize solutions that: 
                a) Match extracted entities and relationships
                b) Pass all validation checks
                c) Use appropriate mathematical modeling
            - Extract ONLY the numerical answer (integer or decimal)
            - Strip all units, text, and formatting — output pure number
            - If uncertainty remains, choose most conservative plausible answer""",
            contexts_list=validated_solutions
        )

        # Clean and extract final numerical answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_synthesis.strip())
        
        # Handle edge case: if multiple numbers, take first (most likely the answer)
        if ' ' in cleaned_answer:
            cleaned_answer = cleaned_answer.split()[0]
            
        return cleaned_answer