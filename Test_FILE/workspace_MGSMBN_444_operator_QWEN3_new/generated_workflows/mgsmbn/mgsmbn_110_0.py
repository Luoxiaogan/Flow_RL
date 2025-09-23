# Workflow ID: mgsmbn_110_0
# Benchmark: mgsmbn
# Data Indices: [111, 130]

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

        # PHASE 1: INITIAL CLASSIFICATION & DECOMPOSITION
        classification = await self.generate(
            instruction="""Thoroughly classify this Bengali math problem. Identify:
            1. Problem type: Sequential, Proportional, Distribution, Comparison, Rate, or Multi-entity
            2. Key entities: People, objects, quantities mentioned
            3. Temporal markers: Does it involve days, steps, or sequences?
            4. Mathematical operations hinted: Fractions, percentages, addition chains, etc.
            5. Units involved: টাকা, ফুট, জিনিস, etc.
            6. Answer constraints: Must be integer? Non-negative? Decimal allowed?
            Output in structured JSON-like format for easy parsing.""",
            context=""
        )

        # PHASE 2: PARALLEL DECOMPOSITION FROM MULTIPLE ANGLES
        decomposition_tasks = [
            self.generate(
                instruction=f"""Mathematical Decomposition:
                Based on classification: {classification}
                Extract all numerical values and their semantic roles.
                Build step-by-step calculation sequence.
                Identify dependencies: What must be calculated before what?
                Flag any ambiguous references or hidden steps.
                Format as numbered steps with justifications.""",
                context=""
            ),
            self.generate(
                instruction=f"""Linguistic Decomposition:
                Analyze Bengali phrasing for mathematical intent.
                Map phrases like 'দুই তৃতীয়াংশ', 'আরও X বেশি', 'বাকির Y অংশ' to operations.
                Identify subject-verb-object relationships that imply calculations.
                Highlight any idiomatic expressions that might mislead literal translation.
                Output as annotated text with operation tags.""",
                context=""
            ),
            self.generate(
                instruction=f"""Chronological Decomposition:
                If problem involves time or sequence (দিন, পরে, আগে, তারপর), build timeline.
                For each time point, state known quantities and derived quantities.
                Show how values propagate through time.
                If no time element, state 'N/A' and focus on logical dependency chain instead.
                Format as timeline table or dependency graph.""",
                context=""
            )
        ]

        decompositions = await asyncio.gather(*decomposition_tasks)

        # PHASE 3: VALIDATION & REVISION LOOP
        validated_decompositions = []
        for decomp in decompositions:
            current = decomp
            for iteration in range(3):  # Max 3 revision cycles
                validation = await self.generate(
                    instruction=f"""CRITICAL VALIDATION CHECK:
                    Examine this decomposition for:
                    1. Arithmetic consistency: Do intermediate steps add up?
                    2. Unit consistency: Are units preserved or converted correctly?
                    3. Contextual plausibility: No negative unicorns, fractional people unless allowed.
                    4. Dependency correctness: Is operation order logically sound?
                    5. Completeness: Are all problem elements addressed?
                    If errors found, describe them precisely. If clean, say 'VALIDATED'.""",
                    context=current
                )
                
                if "VALIDATED" in validation or iteration == 2:  # Last iteration
                    validated_decompositions.append(current)
                    break
                else:
                    current = await self.revise(
                        instruction=f"""REVISE BASED ON VALIDATION:
                        Validation feedback: {validation}
                        Fix all identified errors.
                        Preserve correct parts.
                        Add explicit unit tracking if missing.
                        Clarify ambiguous steps.
                        Ensure final answer format matches problem constraints.""",
                        context=current
                    )

        # PHASE 4: ENSEMBLE SYNTHESIS
        synthesized = await self.ensemble(
            instruction="""SYNTHESIZE MULTIPLE PERSPECTIVES:
            You have 3 validated decompositions of the same problem:
            1. Mathematical (step-by-step calc)
            2. Linguistic (Bengali phrase → operation mapping)
            3. Chronological/Logical (sequence/timeline)
            
            Your task:
            - Identify consensus calculations (appearing in 2+ decompositions)
            - Resolve conflicts by choosing most contextually grounded approach
            - Build unified solution path that incorporates all valid insights
            - Output FINAL ANSWER as single numerical value at end, prefixed by 'ANSWER: '
            - Include brief justification tracing back to problem text""",
            contexts_list=validated_decompositions
        )

        # PHASE 5: FINAL SANITY CHECK & EXTRACTION
        final_answer = await self.generate(
            instruction=f"""FINAL SANITY CHECK & ANSWER EXTRACTION:
            Given synthesized solution: {synthesized}
            
            Verify:
            1. Answer is single numerical value (integer or decimal as appropriate)
            2. Matches unit and type constraints from initial classification
            3. Passes real-world plausibility test (no negative counts, etc.)
            4. Directly answers the question asked
            
            If valid, output ONLY the numerical value (no text, no units).
            If invalid, recalculate using most reliable decomposition path.""",
            context=synthesized
        )

        # Extract pure number using regex to handle any residual text
        match = re.search(r'[\d\.]+', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return as-is if no number found (let grading handle it)
            return final_answer.strip()