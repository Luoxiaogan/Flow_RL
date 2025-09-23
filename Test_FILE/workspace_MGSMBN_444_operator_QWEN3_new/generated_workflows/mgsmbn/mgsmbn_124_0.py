# Workflow ID: mgsmbn_124_0
# Benchmark: mgsmbn
# Data Indices: [67, 158]

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

        # PHASE 1: DIAGNOSTIC CLASSIFICATION & ENTITY EXTRACTION (Parallel Fork)
        diagnostic_tasks = [
            self.generate(
                instruction="""Thoroughly analyze the Bengali word problem and classify its structure. Identify:
                1. Problem type: Sequential, Proportional, Distribution, Comparison, Multi-entity, or Rate-based
                2. Complexity level: Linear (single equation), Recursive (multi-step dependencies), or Constraint-heavy (multiple conditions)
                3. Key mathematical operations required: Addition, Subtraction, Multiplication, Division, Fractions, Percentages, Algebra
                4. Real-world constraints: Non-negative quantities, integer-only answers, unit consistency
                5. Hidden steps: Any unstated intermediate calculations needed
                Format as a structured JSON-like schema with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all named entities, numerical values, and their relationships from the Bengali text. Specifically:
                - List all people/objects mentioned and their roles
                - Extract every number and what it quantifies (e.g., "88,000 copies", "three times")
                - Map relationships: "A is X times B", "C after D", "E less than F"
                - Identify the unknown: What is being asked for?
                Present as a clean, labeled list with no markdown.""",
                context=""
            )
        ]
        
        diagnostic_results = await asyncio.gather(*diagnostic_tasks)
        classification, entities = diagnostic_results[0], diagnostic_results[1]

        # PHASE 2: CONTEXT COMPRESSION & SCHEMA BUILDING
        problem_schema = await self.summarize(
            instruction="""Synthesize the classification and entity extraction into a single, compact problem schema. Include:
            - Problem type and complexity
            - All variables and their relationships (use algebraic notation where possible)
            - Known values and units
            - Unknown to solve for
            - Critical constraints
            Keep it under 200 words but preserve all mathematical essence.""",
            context=f"CLASSIFICATION:
{classification}

ENTITIES:
{entities}"
        )

        # PHASE 3: PARALLEL SOLUTION STRATEGIES (Diamond Pattern)
        solution_strategies = [
            self.generate(
                instruction=f"""Solve using ALGEBRAIC MODELING:
                Given schema: {problem_schema}
                1. Define variables for unknowns
                2. Write equations representing all relationships
                3. Solve step-by-step with clear substitutions
                4. Box final answer as ### <number> ###
                Show all work. Verify against constraints.""",
                context=problem_schema
            ),
            self.generate(
                instruction=f"""Solve using NARRATIVE PROGRESSION:
                Given schema: {problem_schema}
                1. Reconstruct the story chronologically
                2. Calculate quantities at each story beat
                3. Track units and carry forward intermediate results
                4. Box final answer as ### <number> ###
                Explain each step in simple Bengali-to-English translated logic.""",
                context=problem_schema
            ),
            self.generate(
                instruction=f"""Solve using UNIT & DIMENSION ANALYSIS:
                Given schema: {problem_schema}
                1. Identify all units (টাকা, ঘণ্টা, জিনিস, etc.)
                2. Ensure unit consistency at every operation
                3. Use dimensional analysis to verify relationships
                4. Box final answer as ### <number> ###
                Highlight any unit conversions or consistency checks.""",
                context=problem_schema
            )
        ]
        
        raw_solutions = await asyncio.gather(*solution_strategies)

        # PHASE 4: SOLUTION SYNTHESIS & VALIDATION (Ensemble + Iterative Refinement)
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution attempts into one authoritative answer. Evaluate based on:
            1. Mathematical correctness (does it satisfy all equations/relationships?)
            2. Unit consistency (are units preserved and appropriate?)
            3. Narrative fidelity (does it match the story's logic?)
            4. Constraint adherence (non-negative, integer if required, etc.)
            If solutions conflict, prioritize the one with explicit unit tracking and step-by-step verification.
            Extract ONLY the final numerical answer in format: ### <number> ###""",
            contexts_list=raw_solutions
        )

        # PHASE 5: VALIDATION LOOP (Up to 3 iterations)
        current_solution = synthesized_solution
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Rigorously validate this solution against the original problem:
                Solution: {current_solution}
                Original Schema: {problem_schema}
                
                Check:
                1. Does the answer satisfy ALL stated conditions?
                2. Are there any arithmetic errors in the derivation?
                3. Does it violate real-world constraints (e.g., negative people, fractional items when inappropriate)?
                4. Is the unit correct and consistent?
                5. Does it match the problem's asked quantity?
                
                If valid, respond ONLY with "VALID".
                If invalid, explain the error concisely and suggest correction.""",
                context=current_solution
            )
            
            if "VALID" in validation.upper():
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix the following error:
                    Validation Feedback: {validation}
                    
                    Requirements:
                    - Maintain the ### <number> ### format
                    - Correct the mathematical or logical flaw
                    - Preserve unit consistency
                    - Re-verify against all constraints""",
                    context=current_solution
                )
        else:
            # Fallback: Extract number via regex if validation loop exhausted
            numbers = re.findall(r'###\s*([\d,]+\.?\d*)\s*###', current_solution)
            if numbers:
                current_solution = f"### {numbers[0]} ###"

        # PHASE 6: FINAL EXTRACTION & OUTPUT
        final_answer = await self.summarize(
            instruction="""Extract ONLY the numerical answer from the solution. 
            Remove all text, units, and markdown. 
            If the answer is in ### <number> ### format, return just the number.
            Ensure no commas or extra spaces. Return as plain string.""",
            context=current_solution
        )
        
        # Clean and return
        clean_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        return clean_answer