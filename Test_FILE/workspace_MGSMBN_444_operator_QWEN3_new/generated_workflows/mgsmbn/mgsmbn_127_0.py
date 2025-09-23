# Workflow ID: mgsmbn_127_0
# Benchmark: mgsmbn
# Data Indices: [117]

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

        # PHASE 1: PARALLEL PERSPECTIVE EXTRACTION
        # Extract numerical entities, logical relationships, and problem archetype simultaneously
        data_lens, logic_lens, pattern_lens = await asyncio.gather(
            self.generate(
                instruction="""Extract ALL numerical values, units, and named entities with precision:
                - List every number with its contextual descriptor (e.g., "3 customers", "$2 per bottle")
                - Identify measurement units (টাকা, ঘণ্টা, জিনিস) and their relationships
                - Flag any ambiguous quantities that need disambiguation
                - Format as bullet points with clear labeling""",
                context=""
            ),
            self.generate(
                instruction="""Map temporal/causal relationships and operation sequence:
                - Identify chronological order of events (first this happens, then that)
                - Extract conditional statements ("if", "when", "after")
                - Determine calculation dependencies (what must be computed before what)
                - Represent as numbered steps with dependency arrows""",
                context=""
            ),
            self.generate(
                instruction="""Classify mathematical archetype and solution framework:
                - Determine problem type: rate, distribution, comparison, multi-entity, etc.
                - Identify governing formulas or proportional relationships
                - Specify required operations (addition chain, percentage calculation, unit conversion)
                - Output template: "Archetype: [type]. Framework: [formula]. Operations: [list]" """,
                context=""
            )
        )

        # PHASE 2: CONSTRAINT SYNTHESIS & MODEL UNIFICATION
        unified_model = await self.ensemble(
            instruction="""Synthesize perspectives into coherent problem model:
            1. Cross-validate numerical data against logical sequence - flag inconsistencies
            2. Map pattern classification onto entity relationships - ensure formula applicability
            3. Resolve unit conflicts by dimensional analysis (e.g., verify $/bottle × bottles = $)
            4. Prioritize: Numerical accuracy > Temporal logic > Pattern classification
            5. Output unified model with: Entities, Operations Sequence, Governing Formula, Unit Tracking""",
            contexts_list=[data_lens, logic_lens, pattern_lens]
        )

        # PHASE 3: SOLUTION GENERATION WITH DIMENSIONAL ANALYSIS
        raw_solution = await self.generate(
            instruction=f"""Generate step-by-step solution with embedded unit tracking:
            Using unified model: {unified_model}
            
            Requirements:
            - For EACH calculation step: 
              a) State input values with units 
              b) Show operation with dimensional analysis 
              c) Output result with derived units
            - Maintain running unit consistency check
            - Highlight any unit conversions performed
            - Final answer must emerge from dimensional cancellation
            - If fractional entities appear (e.g., 2.5 people), reinterpret contextually""",
            context=unified_model
        )

        # PHASE 4: ADVERSARIAL VALIDATION (PARALLEL)
        arithmetic_validator, contextual_validator = await asyncio.gather(
            self.generate(
                instruction=f"""Validate arithmetic via symbolic re-derivation:
                - Re-express problem as algebraic equations using variables
                - Solve symbolically first, then substitute numbers
                - Verify each numerical step against symbolic result
                - Flag any discrepancy > 0.01% as error
                - Output: "Verified" or "Error at step X: [description]" """,
                context=raw_solution
            ),
            self.generate(
                instruction=f"""Validate contextual plausibility:
                - Check if answer makes real-world sense (e.g., no negative profits, fractional people)
                - Verify scale appropriateness (e.g., $20 profit reasonable for 8 customers?)
                - Ensure no information from original problem was ignored
                - Output: "Plausible" or "Implausible: [reason]" """,
                context=raw_solution
            )
        )

        # PHASE 5: ERROR-CORRECTING ENSEMBLE
        validation_result = await self.ensemble(
            instruction="""Decide solution validity and trigger correction if needed:
            - If BOTH validators say valid: Output solution as-is
            - If EITHER validator flags error: Initiate targeted revision
            - Revision focus: Address specific error type (arithmetic vs contextual)
            - Never proceed with unvalidated solution""",
            contexts_list=[raw_solution, arithmetic_validator, contextual_validator]
        )

        # CONDITIONAL REVISION LOOP (MAX 1 ITERATION)
        if "error" in validation_result.lower() or "implausible" in validation_result.lower():
            refined_solution = await self.revise(
                instruction=f"""Correct identified errors while preserving valid structure:
                Validation feedback: {validation_result}
                Original solution: {raw_solution}
                
                Rules:
                - Only modify erroneous components
                - Maintain dimensional analysis rigor
                - Revalidate unit consistency after changes
                - If contextual error: reinterpret ambiguous phrases
                - Output complete corrected solution with change log""",
                context=raw_solution
            )
            final_output = refined_solution
        else:
            final_output = validation_result

        # PHASE 6: ANSWER EXTRACTION & FORMATTING
        final_answer = await self.generate(
            instruction=f"""Extract numerical answer with verification trail:
            From solution: {final_output}
            
            Requirements:
            - Isolate final numerical value (integer or decimal)
            - Verify it matches dimensional analysis conclusion
            - Confirm no unit conversion errors in final step
            - Output ONLY the number - no text, no units, no explanation
            - If multiple numbers exist, select the one answering the explicit question""",
            context=final_output
        )

        # CLEAN EXTRACTION (REMOVE NON-NUMERIC CHARACTERS)
        # Handle cases where LLM adds text despite instructions
        cleaned_answer = re.sub(r'[^\d.-]', '', final_answer.strip())
        
        return cleaned_answer