# Workflow ID: mgsmbn_59_0
# Benchmark: mgsmbn
# Data Indices: [48]

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

        # STEP 1: CLASSIFY PROBLEM TYPE AND STRUCTURE
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify it along these dimensions:
            1. Mathematical Operation Type: Is it sequential, proportional, comparative, distributional, or rate-based?
            2. Temporal Structure: Does it involve time progression, repetition, or duration scaling?
            3. Entity Involvement: How many distinct actors/objects are involved? Do their states change?
            4. Unit Handling: What units are present (টাকা, ঘণ্টা, জিনিস, etc.)? Are conversions needed?
            5. Hidden Steps: Are there implied calculations not explicitly stated?
            6. Answer Format: Should the answer be integer, decimal, or fraction?
            7. Real-World Constraints: Are there physical/social limits (non-negative, whole numbers, etc.)?
            Provide structured classification with clear labels for each dimension.""",
            context=""
        )

        # STEP 2: EXTRACT ENTITY-STATE TRANSITIONS
        state_tracking = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Extract all entities and their state transitions:
            - List each actor/object mentioned
            - For each, note initial state, actions performed, and resulting state
            - Map chronological sequence of events
            - Highlight any conditional branches or constraints
            Format as a numbered timeline with state changes.""",
            context=classification
        )

        # STEP 3: PARALLEL SOLUTION PATH GENERATION (DIAMOND PATTERN)
        literal_path, algebraic_path, unit_path = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using LITERAL NARRATIVE TRANSLATION:
                - Follow the exact sequence of events described in the problem
                - Convert each Bengali sentence directly into a mathematical step
                - Preserve chronological order
                - Show intermediate calculations explicitly
                - Do not skip any implied steps
                Base your reasoning on this state tracking: {state_tracking}""",
                context=state_tracking
            ),
            self.generate(
                instruction=f"""Solve using ALGEBRAIC ABSTRACTION:
                - Ignore narrative sequence; focus on mathematical relationships
                - Define variables for unknowns
                - Set up equations based on proportionalities, totals, or differences
                - Solve symbolically first, then substitute values
                - Show equation derivation and solving steps
                Use this classification context: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using UNIT-CONSISTENCY TRACKING:
                - Identify all units in the problem
                - Track unit transformations at each calculation step
                - Flag any unit mismatches or needed conversions
                - Ensure final answer has correct unit dimension
                - Verify dimensional analysis at each operation
                Reference this state tracking: {state_tracking}""",
                context=state_tracking
            )
        )

        # STEP 4: ENSEMBLE SYNTHESIS WITH CONFLICT RESOLUTION
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution paths:
            1. Identify points of agreement across all three solutions
            2. Where they disagree, trace back to the specific step causing divergence
            3. Reconstruct a hybrid solution that:
               - Preserves correct elements from each path
               - Resolves contradictions by re-examining original problem constraints
               - Flags any remaining ambiguities
            4. Present final step-by-step solution with clear justification for each step
            Prioritize solutions that maintain unit consistency and respect real-world constraints.""",
            contexts_list=[literal_path, algebraic_path, unit_path]
        )

        # STEP 5: REALITY CHECK AND REVISION
        validated_solution = await self.revise(
            instruction="""Perform REALITY CHECK on the synthesized solution:
            - Does the final answer make sense in real-world context?
            - Check for: negative quantities (invalid for time/items), fractional people, 
              unreasonable magnitudes (e.g., 1000 hours of TV), unit mismatches
            - Verify against problem's implicit constraints (e.g., 'half' implies division by 2)
            - If any red flags, revise calculations with corrected assumptions
            - Ensure answer format matches problem requirements (integer/decimal)""",
            context=synthesized_solution
        )

        # STEP 6: FINAL ANSWER EXTRACTION AND FORMATTING
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the validated solution:
            - Remove all units, explanations, and intermediate steps
            - If decimal, round to 2 places ONLY if problem implies approximation
            - Otherwise, preserve exact value (integer or fraction)
            - Output must be a single number, nothing else
            - If multiple answers possible, choose most contextually appropriate
            - Verify this matches the original problem's question""",
            context=validated_solution
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        # Handle edge case: if empty or invalid, return 0 (fallback)
        if not cleaned_answer:
            return "0"
            
        return cleaned_answer