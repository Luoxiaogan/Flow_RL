# Workflow ID: mgsmbn_67_0
# Benchmark: mgsmbn
# Data Indices: [83, 153]

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

        # PHASE 1: PARALLEL SEMANTIC EXTRACTION
        # Extract problem structure from 3 complementary perspectives
        extraction_tasks = [
            self.generate(
                instruction="""Perform mathematical entity extraction:
                - Identify ALL numerical values and their associated units (টাকা, পাউন্ড, টুকরো, etc.)
                - Extract fractions, percentages, ratios with their referents
                - Note temporal markers (প্রতিদিন, প্রতি সপ্তাহে, পরে, আগে)
                - Identify the unknown being asked for
                - Format as structured bullet points with clear labels""",
                context=""
            ),
            self.generate(
                instruction="""Perform narrative sequence extraction:
                - Identify all agents (people, animals, objects) and their actions
                - Chronologically order events as described in the story
                - Note dependencies between actions (e.g., 'after X, Y happened')
                - Highlight implicit constraints from context (e.g., 'remaining' implies subtraction)
                - Format as numbered sequence of events with agent-action-object triples""",
                context=""
            ),
            self.generate(
                instruction="""Perform constraint and unit analysis:
                - List all explicit and implicit constraints (non-negative, integer-only, unit conversions)
                - Identify required unit transformations (weeks to days, fractions to decimals)
                - Note boundary conditions (minimum/maximum values, physical impossibilities)
                - Flag any ambiguous phrases that could have multiple interpretations
                - Format as categorized list with 'Constraints', 'Unit Rules', 'Ambiguities' sections""",
                context=""
            )
        ]
        
        entity_analysis, narrative_analysis, constraint_analysis = await asyncio.gather(*extraction_tasks)

        # PHASE 2: ENSEMBLE SYNTHESIS INTO UNIFIED PROBLEM MODEL
        unified_model = await self.ensemble(
            instruction="""Synthesize these three analyses into a single coherent problem representation:
            1. Combine mathematical entities with their narrative context
            2. Resolve any contradictions by prioritizing mathematical consistency
            3. Integrate constraints and unit rules into the event sequence
            4. Disambiguate any flagged ambiguities by choosing the interpretation that yields integer results or aligns with common problem patterns
            5. Explicitly state the final problem to solve in mathematical terms
            6. Format as: 'PROBLEM: [mathematical formulation]', 'CONSTRAINTS: [list]', 'UNKNOWN: [what to solve for]'""",
            contexts_list=[entity_analysis, narrative_analysis, constraint_analysis]
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION WITH DIVERSE STRATEGIES
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using CHRONOLOGICAL SIMULATION:
                Based on unified model: {unified_model}
                
                - Simulate the problem step-by-step exactly as events unfold in narrative
                - Show intermediate calculations after each step
                - Track units and quantities at each stage
                - Verify no step violates constraints
                - Box final answer at end""",
                context=unified_model
            ),
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
                Based on unified model: {unified_model}
                
                - Define variables for unknowns
                - Write equations representing relationships
                - Solve system step-by-step showing algebraic manipulations
                - Substitute known values and simplify
                - Verify solution satisfies all constraints
                - Box final answer at end""",
                context=unified_model
            ),
            self.generate(
                instruction=f"""Solve using UNIT PROPAGATION & DIMENSIONAL ANALYSIS:
                Based on unified model: {unified_model}
                
                - Start with given quantities and their units
                - Apply operations while tracking unit transformations
                - Use dimensional analysis to verify each step's validity
                - Convert units as needed (weeks→days, fractions→decimals)
                - Ensure final answer has correct unit and format
                - Box final answer at end""",
                context=unified_model
            )
        )

        # PHASE 4: PARALLEL VALIDATION OF SOLUTIONS
        validation_tasks = []
        for i, solution in enumerate(solution_attempts):
            validation_tasks.append(
                self.generate(
                    instruction=f"""CRITICALLY VALIDATE THIS SOLUTION:
                    Solution {i+1}: {solution}
                    
                    Check for:
                    1. Mathematical correctness of each calculation step
                    2. Unit consistency throughout (no unit mismatches)
                    3. Adherence to all constraints (integer values where required, non-negative, etc.)
                    4. Narrative plausibility (does it match the story's logic?)
                    5. Final answer format (single numerical value, no text/units)
                    
                    If valid, respond 'VALID: [final numerical answer]'
                    If invalid, respond 'INVALID: [specific reason]'""",
                    context=solution
                )
            )
        
        validations = await asyncio.gather(*validation_tasks)

        # Extract valid answers
        valid_answers = []
        for validation in validations:
            if "VALID:" in validation:
                # Extract number from "VALID: 500" or similar
                match = re.search(r'VALID:\s*([0-9]+\.?[0-9]*)', validation)
                if match:
                    valid_answers.append(match.group(1))

        # PHASE 5: ENSEMBLE FINAL ANSWER OR TRIGGER REFINEMENT
        if len(valid_answers) >= 2:
            # Consensus among multiple valid solutions
            final_answer_str = await self.ensemble(
                instruction="""Select final answer from these valid candidates:
                - If all agree, return that value
                - If conflict, choose the one that best satisfies constraints and narrative
                - Output ONLY the numerical value, nothing else""",
                contexts_list=valid_answers
            )
        elif len(valid_answers) == 1:
            final_answer_str = valid_answers[0]
        else:
            # No valid solutions - trigger refinement
            refinement_tasks = []
            for i, (solution, validation) in enumerate(zip(solution_attempts, validations)):
                refinement_tasks.append(
                    self.revise(
                        instruction=f"""REVISE SOLUTION BASED ON VALIDATION FEEDBACK:
                        Original solution: {solution}
                        Validation feedback: {validation}
                        
                        Common issues to fix:
                        - Convert fractional results to integers if context requires whole units
                        - Re-calculate with proper unit conversions
                        - Ensure chronological steps match narrative sequence
                        - Check arithmetic operations for sign errors
                        - Re-express answer as single numerical value
                        
                        Output revised solution with boxed final answer""",
                        context=solution
                    )
                )
            
            refined_solutions = await asyncio.gather(*refinement_tasks)
            
            # Validate refined solutions
            refined_validations = []
            for solution in refined_solutions:
                refined_validations.append(
                    self.generate(
                        instruction=f"""FINAL VALIDATION:
                        Solution: {solution}
                        
                        Same criteria as before. Respond 'VALID: [number]' or 'INVALID: [reason]'""",
                        context=solution
                    )
                )
            
            refined_validations_results = await asyncio.gather(*refined_validations)
            
            # Extract refined valid answers
            refined_valid_answers = []
            for validation in refined_validations_results:
                if "VALID:" in validation:
                    match = re.search(r'VALID:\s*([0-9]+\.?[0-9]*)', validation)
                    if match:
                        refined_valid_answers.append(match.group(1))
            
            if refined_valid_answers:
                final_answer_str = refined_valid_answers[0]  # Take first valid refined answer
            else:
                # Fallback: take first solution's numerical value as last resort
                first_solution = solution_attempts[0]
                match = re.search(r'([0-9]+\.?[0-9]*)', first_solution)
                final_answer_str = match.group(1) if match else "0"

        # PHASE 6: FINAL OUTPUT CLEANUP
        final_answer = await self.revise(
            instruction="""Extract ONLY the numerical answer from this text.
            Remove all units, labels, explanations, and formatting.
            Return a clean number (integer or decimal) and nothing else.
            If multiple numbers exist, choose the one that answers the original question.""",
            context=final_answer_str
        )

        # Ensure it's a clean number
        clean_match = re.search(r'([0-9]+\.?[0-9]*)', final_answer)
        return clean_match.group(1) if clean_match else "0"