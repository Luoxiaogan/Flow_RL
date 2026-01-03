# Workflow ID: mgsmbn_57_0
# Benchmark: mgsmbn
# Data Indices: [62]

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

        # PHASE 1: PARALLEL INTERPRETATION GENERATION
        # Generate three orthogonal interpretations: chronological, structural, unit-tracked
        chron_interpretation, struct_interpretation, unit_interpretation = await asyncio.gather(
            self.generate(
                instruction="""Perform chronological event decomposition:
                1. Identify every event in the order it occurred.
                2. For each event, state: (a) what changed, (b) by how much, (c) the operation (+/-/×/÷).
                3. Maintain running totals after each event.
                4. Flag any ambiguous temporal references.
                Format as numbered steps with intermediate calculations.""",
                context=""
            ),
            self.generate(
                instruction="""Construct mathematical dependency graph:
                1. Identify all quantities and their relationships (equations, proportions, constraints).
                2. Represent as algebraic expressions with variables for unknowns.
                3. Solve symbolically first, then substitute values.
                4. Show derivation path from givens to unknown.
                Format as equation tree with substitution steps.""",
                context=""
            ),
            self.generate(
                instruction="""Track units and entity ownership:
                1. Annotate every number with: (a) unit (টাকা, স্টিকার, etc.), (b) owner/entity, (c) event association.
                2. Validate unit consistency in every operation.
                3. Flag any unit mismatches or unattributed quantities.
                4. Ensure final answer has correct unit and entity.
                Format as annotated ledger with validation checks.""",
                context=""
            )
        )

        # PHASE 2: PARALLEL REVISION WITH BACKWARD VALIDATION
        # Revise each interpretation by simulating backward from answer
        chron_revised, struct_revised, unit_revised = await asyncio.gather(
            self.revise(
                instruction="""Validate chronologically:
                1. Start from your computed final answer.
                2. Reverse each event in chronological order.
                3. Verify you arrive back at initial state.
                4. If not, identify which event was misinterpreted.
                5. Correct and recompute.
                Return corrected step-by-step with validation trail.""",
                context=chron_interpretation
            ),
            self.revise(
                instruction="""Validate structurally:
                1. Take your final expression.
                2. Substitute answer back into original equations.
                3. Verify all constraints are satisfied.
                4. If not, identify which relationship was mis-modeled.
                5. Correct and resolve.
                Return corrected derivation with constraint checks.""",
                context=struct_interpretation
            ),
            self.revise(
                instruction="""Validate unit/entity consistency:
                1. Check every operation for unit compatibility.
                2. Verify entity ownership is preserved (e.g., can't give what you don't have).
                3. Ensure no fractional entities where inappropriate.
                4. Flag and correct any violations.
                Return corrected ledger with unit/entity audit trail.""",
                context=unit_interpretation
            )
        )

        # PHASE 3: ENSEMBLE SYNTHESIS WITH CROSS-EXAMINATION
        final_answer = await self.ensemble(
            instruction="""Synthesize through cross-examination:
            You have three solution attempts:
            1. Chronological with backward validation
            2. Structural with constraint checking
            3. Unit/entity tracked with audit
            
            Perform:
            STEP 1: Identify consensus - where do all three agree? (This is your anchor)
            STEP 2: Diagnose disagreements - what caused divergence? (Linguistic ambiguity? Operation error?)
            STEP 3: Simulate edge cases for disputed interpretations.
            STEP 4: Select or synthesize the most contextually defensible answer.
            STEP 5: Express final answer as NUMBER ONLY (no units, no text).
            
            CRITICAL: If solutions fundamentally disagree or yield implausible results (negative, fractional people), 
            return the most conservative estimate with highest contextual plausibility.""",
            contexts_list=[chron_revised, struct_revised, unit_revised]
        )

        # PHASE 4: SANITY CHECK VIA INVERSE PROBLEM GENERATION
        sanity_check = await self.generate(
            instruction=f"""SANITY CHECK:
            Assume the answer is {final_answer}.
            Now, generate a MINIMAL Bengali word problem that would naturally yield this answer.
            Compare to original problem:
            - Does it preserve key entities and relationships?
            - Is the mathematical structure equivalent?
            - Would a Bengali-speaking child interpret it the same way?
            
            If mismatch > 30%, flag for reanalysis. Otherwise, confirm answer.
            RETURN ONLY THE NUMBER {final_answer} if confirmed, or 'REANALYZE' if not.""",
            context=""
        )

        # PHASE 5: CONDITIONAL REANALYSIS (if sanity check fails)
        if "REANALYZE" in sanity_check.upper():
            # Trigger deeper linguistic reanalysis
            linguistic_focus = await self.generate(
                instruction="""Reanalyze with linguistic precision:
                Focus ONLY on ambiguous phrases in original problem.
                For each ambiguous segment:
                1. List all plausible interpretations.
                2. For each, state supporting evidence from context.
                3. Rank by likelihood.
                4. Recompute answer for top interpretation.
                Return only the recomputed number.""",
                context=f"Original interpretations showed inconsistency. Sanity check failed for: {final_answer}"
            )
            return linguistic_focus.strip()
        
        # Extract number from sanity check (in case it includes confirmation text)
        number_match = re.search(r'[-+]?\d*\.\d+|\d+', sanity_check)
        if number_match:
            return number_match.group(0)
        
        return final_answer.strip()