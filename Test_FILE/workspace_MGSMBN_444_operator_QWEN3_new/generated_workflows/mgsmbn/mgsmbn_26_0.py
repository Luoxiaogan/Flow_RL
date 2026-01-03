# Workflow ID: mgsmbn_26_0
# Benchmark: mgsmbn
# Data Indices: [128, 35]

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

        # PHASE 1: PARALLEL SEMANTIC DECOMPOSITION
        # Extract entities, relationships, and constraints independently
        entity_extraction, relationship_extraction, constraint_extraction = await asyncio.gather(
            self.generate(
                instruction="""Extract all numerical entities and their semantic roles:
                - Identify every number and what it represents (e.g., "4টি কলম" → quantity: 4, object: pens)
                - Map Bengali measurement units to standard forms (টাকা → BDT, টুকরো → units, ঘণ্টা → hours)
                - List named entities (people, places) and their associated quantities
                - Format as structured bullet points with clear labels""",
                context=""
            ),
            self.generate(
                instruction="""Extract mathematical relationships and operations:
                - Identify verbs indicating operations (কিনেছিলেন → addition to cost, বিক্রি করেছিলেন → subtraction from stock)
                - Detect comparative phrases (বেশি, কম, সমান) implying inequalities or equalities
                - Flag sequential markers (প্রথমে, তারপর, শেষে) indicating operation order
                - Translate Bengali operational phrases to mathematical symbols (+, -, ×, ÷, =)
                - Format as equation templates with placeholders""",
                context=""
            ),
            self.generate(
                instruction="""Extract implicit constraints and real-world boundaries:
                - Identify physical impossibilities (negative quantities, fractional people)
                - Note unit consistency requirements (can't add hours to rupees)
                - Flag contextual assumptions (e.g., "সব কলম একই দামে" → uniform pricing)
                - Highlight boundary conditions (minimum/maximum values implied)
                - Format as constraint list with severity levels (MUST, SHOULD)""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE INTO MATHEMATICAL MODEL
        mathematical_model = await self.ensemble(
            instruction="""Synthesize these three analyses into a unified mathematical model:
            1. Combine entities and relationships to define known variables and target unknown
            2. Incorporate constraints to bound solution space
            3. Construct step-by-step calculation sequence or algebraic equation
            4. Annotate each step with units and justification
            5. Flag any unresolved ambiguities or conflicting interpretations
            Output format: 
            TARGET: [unknown variable]
            KNOWN: [list with values and units]
            STEPS: [numbered sequence with operations]
            CONSTRAINTS: [enforced boundaries]
            AMBIGUITIES: [if any]""",
            contexts_list=[entity_extraction, relationship_extraction, constraint_extraction]
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION
        # Three different solving strategies for robustness
        arithmetic_approach, algebraic_approach, unit_tracking_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using step-by-step arithmetic simulation:
                - Start from initial state described in problem
                - Apply each operation sequentially as implied by narrative
                - Show intermediate totals after each step
                - Verify unit consistency at every operation
                - Double-check final answer against constraints
                - Format: Step 1: [operation] → [result] [units] ... Final Answer: [number]""",
                context=mathematical_model
            ),
            self.generate(
                instruction=f"""Solve using algebraic formulation:
                - Define variables for unknowns
                - Write equations based on relationships
                - Solve symbolically showing all steps
                - Substitute known values
                - Simplify to numerical answer
                - Validate against constraints
                - Format: Let x = ... Equation: ... Solution: x = ...""",
                context=mathematical_model
            ),
            self.generate(
                instruction=f"""Solve using unit-first dimensional analysis:
                - Start from target unit (e.g., BDT, units, hours)
                - Work backward to identify required conversions
                - Track unit transformations through each operation
                - Cancel units systematically
                - Arrive at dimensionless numerical answer
                - Format: [Starting unit] → [conversion] → ... → [final number]""",
                context=mathematical_model
            )
        )

        # PHASE 4: COMPRESS SOLUTIONS FOR CONSENSUS
        solution_summaries = await asyncio.gather(
            self.summarize(
                instruction="Extract key steps and final numerical answer. Preserve units and critical justifications. Max 3 sentences.",
                context=arithmetic_approach
            ),
            self.summarize(
                instruction="Extract key steps and final numerical answer. Preserve units and critical justifications. Max 3 sentences.",
                context=algebraic_approach
            ),
            self.summarize(
                instruction="Extract key steps and final numerical answer. Preserve units and critical justifications. Max 3 sentences.",
                context=unit_tracking_approach
            )
        )

        # PHASE 5: CONSENSUS-BASED ANSWER SELECTION
        consensus_solution = await self.ensemble(
            instruction="""You are a math teacher evaluating three solution approaches:
            - Compare logical consistency, arithmetic accuracy, and unit handling
            - Prefer solutions that explicitly address all constraints
            - If all solutions agree, select any and note consensus
            - If they disagree, identify the most rigorous and correct any errors
            - If all contain errors, synthesize a corrected version
            - Final output must include ONLY the numerical answer in this format: ANSWER: [number]""",
            contexts_list=solution_summaries
        )

        # PHASE 6: CONTEXTUAL VALIDATION & REVISION
        validation_check = await self.generate(
            instruction="""Validate this answer against real-world context:
            - Check for negative quantities where impossible (people, items)
            - Verify integer requirement (e.g., number of objects)
            - Confirm unit appropriateness (e.g., decimal hours acceptable, decimal people not)
            - Flag any violations and propose corrected calculation if needed
            - If valid, output 'VALID'
            - If invalid, output 'INVALID: [correction]'""",
            context=consensus_solution
        )

        # Conditional revision if validation fails
        if "INVALID" in validation_check:
            final_solution = await self.revise(
                instruction=f"""Revise the solution based on validation feedback:
                Validation Issue: {validation_check}
                - Correct the calculation while preserving original reasoning structure
                - Ensure unit consistency and contextual plausibility
                - Output ONLY the corrected numerical answer in format: ANSWER: [number]""",
                context=consensus_solution
            )
        else:
            final_solution = consensus_solution

        # PHASE 7: ANSWER EXTRACTION (ENSURE NUMERIC-ONLY OUTPUT)
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - Remove all units, labels, explanations, and formatting
            - Return a clean number (integer or decimal)
            - If multiple numbers exist, select the one labeled as final answer
            - If no clear answer, return 0 as fallback
            OUTPUT FORMAT: [number]""",
            context=final_solution
        )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        return cleaned_answer if cleaned_answer else "0"