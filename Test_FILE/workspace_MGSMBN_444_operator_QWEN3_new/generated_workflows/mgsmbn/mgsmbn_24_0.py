# Workflow ID: mgsmbn_24_0
# Benchmark: mgsmbn
# Data Indices: [157, 198]

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

        # PHASE 1: PARALLEL EXTRACTION - Build multi-perspective understanding
        extraction_instructions = [
            """Extract all mathematical entities with precision:
            - List every number with its contextual meaning (e.g., "8417 = number of men")
            - Identify units (টাকা, পাউন্ড, জন) and ensure they're attached to values
            - Flag any ambiguous or missing units
            - Map relationships: what operations connect these entities?
            - Output as structured bullet points with clear labels""",
            
            """Extract semantic narrative structure:
            - Who are the actors? (people, objects, groups)
            - What actions occur? (buying, dividing, traveling, etc.)
            - What is the temporal sequence? (before/after, initially/finally)
            - What is explicitly asked? (the unknown to solve for)
            - What constraints are implied? (non-negative, integer-only, etc.)
            - Format as a story summary with key events chronologically""",
            
            """Extract operational dependency graph:
            - What must be calculated first? What depends on what?
            - Are there hidden intermediate steps? (unit conversions, percentage calculations)
            - Identify potential pitfalls: mixed units, ambiguous references, unstated assumptions
            - Represent as step-by-step pseudo-code outline
            - Include validation checks at each step"""
        ]

        # Run extractions in parallel
        extraction_results = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in extraction_instructions]
        )

        # PHASE 2: CROSS-VALIDATION & REFINEMENT
        refined_extractions = []
        for i, extraction in enumerate(extraction_results):
            refine_instruction = f"""Critically revise this extraction:
            - Cross-check against original problem for completeness
            - Resolve any ambiguities using context from other perspectives
            - Ensure all numbers and relationships are accounted for
            - Add missing constraints or assumptions with justification
            - Format consistently and eliminate redundancy
            - If confident, append 'VERIFIED' tag; otherwise flag uncertainties
            
            Perspective: {['Mathematical Entities', 'Semantic Narrative', 'Operational Dependencies'][i]}"""
            
            refined = await self.revise(instruction=refine_instruction, context=extraction)
            refined_extractions.append(refined)

        # PHASE 3: PARALLEL SOLUTION ATTEMPTS
        solution_instructions = [
            """Generate solution using mathematical entities perspective:
            - Follow the dependency graph strictly
            - Show all calculations step by step
            - Include unit tracking at each step
            - Box final answer at the end
            - If uncertain, state assumptions explicitly""",
            
            """Generate solution using semantic narrative perspective:
            - Solve as if explaining to a 10-year-old
            - Use the story sequence to guide operations
            - Verify that each step makes narrative sense
            - Check that final answer matches the asked question
            - Include reality-check: does this number make sense?""",
            
            """Generate solution using operational dependencies:
            - Execute the pseudo-code outline literally
            - Validate each intermediate result
            - If validation fails, backtrack and adjust
            - Prioritize precision over speed
            - Document any deviations from initial plan"""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=refined_extractions[i]) 
              for i, instr in enumerate(solution_instructions)]
        )

        # PHASE 4: VALIDATION CASCADE (Iterative Feedback)
        validated_solutions = []
        for attempt in solution_attempts:
            current_solution = attempt
            for iteration in range(3):  # Max 3 refinement cycles
                validator_instruction = """Validate this solution attempt:
                - Plug the final answer back into the original problem
                - Does it satisfy all conditions? 
                - Are units consistent throughout?
                - Are there any arithmetic errors? Recalculate critical steps
                - Does it violate real-world constraints? (e.g., negative people)
                - If errors found, describe exactly what and where
                - If no errors, respond with 'VALID: [answer]'"""
                
                validation = await self.generate(instruction=validator_instruction, context=current_solution)
                
                if "VALID:" in validation:
                    # Extract the validated answer
                    match = re.search(r'VALID:\s*([0-9.,]+)', validation)
                    if match:
                        validated_solutions.append(f"VALIDATED_ANSWER: {match.group(1)}\nSupporting reasoning:\n{current_solution}")
                    else:
                        validated_solutions.append(current_solution)  # Keep as-is if validation format fails
                    break
                else:
                    # Revise based on validation feedback
                    revise_instruction = f"""Fix the solution based on this validation feedback:
                    {validation}
                    
                    - Address all identified errors
                    - Maintain clear step-by-step reasoning
                    - Re-validate critical calculations
                    - Ensure final answer is boxed and unambiguous"""
                    
                    current_solution = await self.revise(instruction=revise_instruction, context=current_solution)
            else:
                # If we exhausted iterations, keep the last version
                validated_solutions.append(current_solution)

        # PHASE 5: ENSEMBLE SYNTHESIS - Merge the best insights
        final_answer = await self.ensemble(
            instruction="""Synthesize the most accurate answer from these attempts:
            - Prioritize solutions marked as VALIDATED
            - If multiple validated answers, check for consensus
            - If disagreement, analyze which approach best handles constraints
            - Extract the numerical answer that is most consistent with all perspectives
            - If all attempts have issues, create a new solution using combined insights
            - Final output must be ONLY the numerical answer (no units, no text)
            - Example: if answer is 6277, output exactly "6277" """,
            contexts_list=validated_solutions
        )

        # Clean the final answer to ensure it's just a number
        # Remove any non-numeric characters except decimal point
        cleaned_answer = re.sub(r'[^\d.]', '', final_answer)
        
        # Handle edge case where multiple numbers might be present
        numbers = re.findall(r'\d+\.?\d*', cleaned_answer)
        if numbers:
            return numbers[0]  # Return first number found
        else:
            # Fallback: return raw ensemble output if cleaning fails
            return final_answer.strip()