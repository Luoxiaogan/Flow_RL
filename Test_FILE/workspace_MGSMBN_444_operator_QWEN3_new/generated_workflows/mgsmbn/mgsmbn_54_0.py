# Workflow ID: mgsmbn_54_0
# Benchmark: mgsmbn
# Data Indices: [25, 156]

import asyncio

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

        # STEP 1: SEMANTIC MODELING - Extract entities, relationships, constraints
        semantic_model = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and construct a structured semantic model. Include:
            1. All named entities (people, objects, places) with their roles
            2. All numerical values with their units and what they quantify
            3. All relationships (comparisons, operations, dependencies) in natural language
            4. The explicit question being asked
            5. Any implicit constraints (non-negative, integer-only, real-world limits)
            6. Identify what is unknown and needs to be calculated
            Format as a clear, labeled markdown structure.""",
            context=""
        )

        # STEP 2: FORMALIZE INTO MATHEMATICAL EXPRESSIONS
        math_model = await self.revise(
            instruction="""Convert the semantic model into formal mathematical expressions:
            - Translate relationships into equations or step-by-step arithmetic operations
            - Annotate every quantity with its unit (টাকা, পাউন্ড, জিনিস, etc.)
            - Make all implicit steps explicit (e.g., "each of 40 restaurants takes 2 pounds" → 40 × 2 = 80)
            - Define variables for unknowns
            - Preserve order of operations as implied by the narrative
            - Flag any unit inconsistencies or dimensional mismatches
            Output only the mathematical model with clear step numbering.""",
            context=semantic_model
        )

        # STEP 3: PARALLEL SOLUTION GENERATION (3 STRATEGIES)
        solution_strategies = [
            """Solve using ALGEBRAIC approach:
            - Set up equations with variables
            - Solve symbolically step by step
            - Substitute known values
            - Show all simplification steps
            - Box final numerical answer""",
            
            """Solve using ARITHMETIC SEQUENTIAL approach:
            - Perform calculations in chronological order as events unfold in the problem
            - Show intermediate results with units
            - Carry units through all operations
            - Verify each step against semantic constraints
            - Box final numerical answer""",
            
            """Solve using VISUAL/PROPORTIONAL approach:
            - Use diagrams, ratios, or proportional reasoning
            - Scale quantities as needed
            - Cross-validate with total constraints
            - Show scaling factors and distribution logic
            - Box final numerical answer"""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{strategy}

                CRITICAL REQUIREMENTS:
                - NEVER output negative quantities for countable items
                - NEVER output fractional people/objects unless explicitly allowed
                - Track units at every step
                - If answer seems counterintuitive, double-check relationship interpretation
                - Final answer must be a single number (integer or decimal)""",
                context=math_model
            ) for strategy in solution_strategies]
        )

        # STEP 4: ENSEMBLE SYNTHESIS - SELECT/MERGE BEST SOLUTION
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution attempts:
            1. Compare numerical results - if all agree, select any
            2. If they disagree, identify which approach best respects:
               - Semantic relationships from original problem
               - Unit consistency
               - Real-world constraints (non-negative, integer where required)
               - Step-by-step logical flow
            3. If two agree and one differs, select the majority if they're consistent with constraints
            4. If all differ, construct a new solution by merging correct elements from each
            5. Output ONLY the final numerical answer in this exact format: "ANSWER: <number>"
            6. If uncertain, choose the most conservative (physically plausible) answer""",
            contexts_list=solution_attempts
        )

        # STEP 5: VALIDATION & REVISION LOOP (max 3 iterations)
        final_answer = synthesized_solution
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Validate this answer against original problem:
                - Does it satisfy all stated relationships?
                - Are units consistent throughout?
                - Does it violate any real-world constraints (negative counts, fractional people)?
                - Is the magnitude reasonable given context?
                - If error found, specify exactly what's wrong and how to fix it
                - If valid, output "VALID" and nothing else""",
                context=final_answer
            )
            
            if "VALID" in validation:
                break
            else:
                final_answer = await self.revise(
                    instruction=f"""REVISE based on validation feedback:
                    Validation feedback: {validation}
                    
                    CORRECTION STRATEGY:
                    1. Re-express the core relationship that was misinterpreted
                    2. Recalculate with corrected interpretation
                    3. Preserve unit tracking
                    4. Ensure answer is single numerical value
                    5. If still uncertain, default to most conservative physically plausible answer
                    Output ONLY the corrected numerical answer in format: "ANSWER: <number>""",
                    context=final_answer
                )
        else:
            # After 3 failed revisions, force extraction of number as last resort
            final_answer = await self.revise(
                instruction="""Extract the single numerical answer from this text, ignoring all other content.
                If multiple numbers exist, choose the one most likely to be the final answer based on context.
                Output ONLY the number, no text.""",
                context=final_answer
            )

        # STEP 6: FINAL EXTRACTION - Ensure pure numerical output
        clean_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - Remove all text, units, labels
            - If decimal, preserve exact precision
            - If fraction, convert to decimal
            - Output nothing but the number
            - If no number found, output "0" as fallback""",
            context=final_answer
        )

        # Clean with regex to ensure pure number
        match = re.search(r'[-+]?\d*\.?\d+', clean_answer)
        if match:
            return match.group(0)
        else:
            return "0"