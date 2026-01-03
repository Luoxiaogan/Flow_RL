# Workflow ID: mgsmbn_44_0
# Benchmark: mgsmbn
# Data Indices: [122]

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

        # Step 1: Semantic Decomposition - Extract entities, relationships, unknowns
        decomposition = await self.generate(
            instruction="""Perform deep semantic decomposition of this Bengali math problem. Identify:
            1. All named entities (people, objects, places)
            2. All numerical values and what they represent
            3. All comparative or relational phrases (e.g., "তিনগুণ বেশি", "অর্ধেক")
            4. The unknown being asked for
            5. Any implicit constraints (e.g., whole numbers for people, non-negative quantities)
            Format as structured JSON with keys: entities, values, relationships, unknown, constraints""",
            context=""
        )

        # Step 2: Generate multiple interpretations in parallel
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret this problem LITERALLY from the Bengali text:
                - Translate relationships exactly as stated
                - Preserve original phrasing intent
                - Do not simplify or assume
                - Output as step-by-step reasoning""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Interpret this problem ALGEBRAICALLY:
                - Assign variables to unknowns
                - Write equations based on relationships
                - Show substitution steps
                - Output as mathematical derivation""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Interpret this problem DIAGRAMMATICALLY (described in text):
                - Imagine a visual representation
                - Describe how quantities relate spatially or comparatively
                - Use analogies if helpful
                - Output as descriptive narrative""",
                context=decomposition
            )
        )

        # Step 3: Ensemble - Synthesize best interpretation
        best_interpretation = await self.ensemble(
            instruction="""Synthesize the most accurate interpretation by:
            1. Comparing fidelity to original Bengali semantics
            2. Checking mathematical consistency
            3. Ensuring all constraints are respected
            4. Prioritizing interpretations that maintain unit consistency and avoid fractional people/items unless explicitly allowed
            5. Selecting the clearest, most educationally appropriate approach for elementary students
            Output the chosen interpretation with justification""",
            contexts_list=interpretations
        )

        # Step 4: Generate step-by-step solution
        raw_solution = await self.generate(
            instruction=f"""Using this interpretation:
            {best_interpretation}
            
            Generate a complete, step-by-step solution:
            - Show all calculations explicitly
            - Justify each step
            - Maintain unit tracking
            - Verify intermediate results
            - Box the final answer at the end""",
            context=best_interpretation
        )

        # Step 5: Parallel validation checks
        validation_tasks = [
            self.generate(
                instruction=f"""Validate unit consistency:
                - Are all quantities in compatible units?
                - Are units carried through all operations?
                - Are final units appropriate for the context?
                Return 'PASS' or 'FAIL: [reason]'""",
                context=raw_solution
            ),
            self.generate(
                instruction=f"""Validate against implicit constraints:
                - No fractional people/objects unless allowed
                - No negative quantities
                - Results make real-world sense
                Return 'PASS' or 'FAIL: [reason]'""",
                context=raw_solution
            ),
            self.generate(
                instruction=f"""Validate arithmetic:
                - Recompute key steps independently
                - Check for calculation errors
                - Verify final answer matches derivation
                Return 'PASS' or 'FAIL: [reason]'""",
                context=raw_solution
            )
        ]
        validation_results = await asyncio.gather(*validation_tasks)

        # Step 6: Revise if any validation fails
        if any("FAIL" in result for result in validation_results):
            revision_context = f"Solution: {raw_solution}

Validations: {'; '.join(validation_results)}"
            refined_solution = await self.revise(
                instruction=f"""Revise this solution to fix all identified issues:
                {revision_context}
                
                - Correct any unit inconsistencies
                - Adjust for constraint violations (e.g., round appropriately)
                - Fix arithmetic errors
                - Maintain educational clarity
                - Preserve step-by-step reasoning""",
                context=raw_solution
            )
        else:
            refined_solution = raw_solution

        # Step 7: Final refinement for clarity and extraction
        final_answer_text = await self.revise(
            instruction="""Extract ONLY the final numerical answer from this solution.
            - Must be a single number (integer or decimal)
            - Remove all units, explanations, and punctuation
            - If multiple numbers appear, select the one that answers the original question
            - If answer is embedded in text, isolate it
            Example: If solution says 'James has 16 friends', output '16'""",
            context=refined_solution
        )

        # Step 8: Clean and return final answer
        # Extract number using regex to handle any residual text
        match = re.search(r'[-+]?\d*\.\d+|\d+', final_answer_text)
        final_answer = match.group(0) if match else "0"

        return final_answer