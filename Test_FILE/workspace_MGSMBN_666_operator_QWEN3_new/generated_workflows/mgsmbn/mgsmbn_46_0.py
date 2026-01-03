# Workflow ID: mgsmbn_46_0
# Benchmark: mgsmbn
# Data Indices: [140, 1]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: LINGUISTIC & SEMANTIC PARSING
        entity_extraction = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem to extract:
            1. All named entities (people, objects, animals) with descriptors
            2. All numerical values with their contextual meaning (e.g., "8 years" not just "8")
            3. All relationships (comparisons, operations, dependencies) in structured form
            4. The explicit question being asked
            5. Any implicit constraints (e.g., ages must be positive, whole birds, etc.)
            
            Format as:
            ENTITIES: [list with descriptors]
            NUMBERS: [value + context]
            RELATIONSHIPS: [subject → predicate → object]
            QUESTION: [verbatim question]
            CONSTRAINTS: [list of implicit rules]
            
            Be meticulous — misidentifying a relationship will cascade into wrong answers.""",
            context=""
        )

        # PHASE 2: PARALLEL SYMBOLIC FORMULATION (Generate 3 candidate interpretations)
        formulation_instructions = [
            """Convert the extracted relationships into mathematical equations or pseudocode.
            Assume all percentage increases are multiplicative (150% increase = 2.5x original).
            Treat named entities as variables. Resolve dependencies chronologically.
            Include unit tracking (টাকা, বছর, etc.) in comments. Show step-by-step symbolic logic.
            If ambiguity exists, choose the most literal interpretation.""",
            
            """Convert relationships into mathematical model with conservative assumptions.
            Where percentages appear, verify if they apply to original value or cumulative value.
            Where ages or quantities are compared, express as algebraic equations.
            Include dimensional analysis — ensure units match on both sides of equations.
            If entities seem unrelated, assume they must be connected through the question's goal.""",
            
            """Create mathematical formulation by focusing on the final question.
            Work backwards from what is asked to what is given.
            Treat all comparative phrases ("older than", "increased by") as difference equations.
            Assume proportional relationships unless explicitly stated otherwise.
            Include sanity checks within the model (e.g., if age < 0, flag error)."""
        ]

        symbolic_models = await asyncio.gather(
            *[self.generate(instruction=instr, context=entity_extraction) 
              for instr in formulation_instructions]
        )

        # PHASE 3: PARALLEL COMPUTATION
        code_solutions = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Generate Python code that computes the answer based on this symbolic model:
                {model}
                
                Requirements:
                - Use exact arithmetic (no floating point unless necessary)
                - Include assertions for constraints (e.g., assert age > 0)
                - Output only the final numerical answer (no text)
                - Handle units internally (convert to base units if needed)
                - If error occurs, return 'ERROR'""",
                context=model
            ) for model in symbolic_models]
        )

        # PHASE 4: CONSTRAINT-VALIDATED ENSEMBLE
        validated_answer = await self.ensemble(
            instruction=f"""Select the best answer from candidates below by validating against constraints:
            Extracted Constraints: {entity_extraction}
            
            Evaluation Criteria:
            1. Does the answer satisfy all explicit numerical relationships?
            2. Does it respect implicit constraints (positive ages, whole entities, etc.)?
            3. Is the unit/dimension consistent with the question's requirement?
            4. Does it match the narrative logic (e.g., if problem says "four birds", answer should reflect sum of four entities)?
            
            Return ONLY the numerical answer that best satisfies all criteria. If all fail, return the least invalid one.""",
            contexts_list=code_solutions
        )

        # PHASE 5: NARRATIVE SANITY CHECK
        sanity_check = await self.generate(
            instruction=f"""Verify the answer {validated_answer} against the original problem's narrative:
            - Does it directly answer the question asked?
            - Does it contradict any explicit statement in the problem?
            - Is it plausible in real-world context (e.g., no negative money, fractional people)?
            - Are all named entities accounted for in the calculation?
            
            Respond ONLY with 'VALID' or 'INVALID'.""",
            context=entity_extraction
        )

        # PHASE 6: FALLBACK REVISION (if sanity check fails)
        if "INVALID" in sanity_check.upper():
            revised_extraction = await self.revise(
                instruction="""Re-analyze the problem with focus on previously misunderstood relationships.
                Common errors to check:
                - Percentage application (150% of original vs 150% increase)
                - Entity mapping (are "four birds" four separate named entities?)
                - Operation order (is multiplication before addition?)
                - Hidden dependencies (does "Sally Four's age equals Sally Thirty-Two's" create equivalence?)
                
                Re-extract entities, relationships, and constraints with extreme precision.""",
                context=entity_extraction
            )

            # Single-path recalculation with revised understanding
            revised_model = await self.generate(
                instruction="""Create mathematical model with corrected understanding.
                Pay special attention to the relationships that likely caused the invalid answer.
                Use algebraic notation with explicit variable definitions.
                Include unit tracking and constraint assertions.""",
                context=revised_extraction
            )

            final_computation = await self.programmer(
                instruction="""Generate Python code from revised model.
                Be extra cautious with operations and dependencies.
                Output only the numerical answer.""",
                context=revised_model
            )
            
            return final_computation.strip()

        return validated_answer.strip()