# Workflow ID: mgsmbn_74_0
# Benchmark: mgsmbn
# Data Indices: [40, 65]

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

        # === PHASE 1: PARALLEL SEMANTIC EXTRACTION ===
        extraction_instructions = [
            """Extract all numerical values, units, entities, and relationships with LITERAL interpretation.
            - List every number and its explicit referent (e.g., "15 pounds" → weight_to_remove=15)
            - Do not infer unstated relationships
            - Preserve fractions and decimals exactly as written
            - Format: Key-value pairs, one per line""",
            
            """Extract all numerical values, units, entities, and relationships with CONTEXTUAL interpretation.
            - Infer implicit relationships (e.g., "remove 15 pounds" implies subtraction)
            - Map entities to roles (e.g., "comic books" → items being removed)
            - Identify goal (what is being asked)
            - Format: Structured JSON-like outline""",
            
            """Extract all numerical values, units, entities, and relationships with UNIT-AWARE interpretation.
            - Track units for every quantity (pounds, hours, items, etc.)
            - Flag unit mismatches or conversions needed
            - Identify dimensional consistency
            - Format: Table with columns: Entity, Value, Unit, Role"""
        ]

        extractions = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in extraction_instructions]
        )

        # === PHASE 2: ENSEMBLE PROBLEM CLASSIFICATION ===
        classification_instruction = """Analyze the extracted information and classify this problem into exactly one primary type:
        - Sequential: Multiple steps in time/order (deposit then withdraw)
        - Rate: Involves speed, work rate, unit price (distance/time, items/hour)
        - Proportional: Ratios, percentages, fractions, scaling (half of, 20% more)
        - Distribution: Dividing, sharing, grouping with remainders (split among, how many each)
        - Comparison: Differences, "how many more", inequalities (more than, less than)
        - Multi-entity: Multiple actors/objects with different quantities (A has X, B has Y)
        
        Also identify:
        - Required operations (add, subtract, multiply, divide, algebra)
        - Constraints (integer only, positive only, unit consistency)
        - Hidden steps (intermediate calculations not stated)
        
        Output format: 
        TYPE: [type]
        OPERATIONS: [list]
        CONSTRAINTS: [list]
        HIDDEN: [yes/no]"""

        problem_analysis = await self.ensemble(
            instruction=classification_instruction,
            contexts_list=extractions
        )

        # === PHASE 3: STRATEGY-SPECIFIC SOLUTION GENERATION ===
        solution_instructions = {
            "Sequential": """Solve using step-by-step chronological modeling.
            - Represent each event as a state change
            - Track cumulative values
            - Show intermediate results after each step
            - Verify final state matches goal
            - Use exact arithmetic, preserve fractions""",
            
            "Rate": """Solve using rate × quantity = total framework.
            - Identify rate (per unit), quantity, and total
            - Set up equation: rate × quantity = total
            - Solve for unknown
            - Check unit consistency (e.g., miles/hour × hours = miles)
            - Handle inverse rates if needed""",
            
            "Proportional": """Solve using proportional relationships.
            - Express ratios as fractions or percentages
            - Set up proportion equation: a/b = c/d
            - Cross-multiply and solve
            - Handle scaling (if doubled, then...)
            - Convert percentages to decimals""",
            
            "Distribution": """Solve using division with quotient and remainder.
            - Identify total quantity and group size
            - Compute: quotient = total // group_size, remainder = total % group_size
            - Interpret remainder contextually (discard, round up, etc.)
            - Ensure integer constraints are respected""",
            
            "Comparison": """Solve using algebraic comparison.
            - Assign variables to unknowns
            - Set up equations based on comparisons (A = B + 8)
            - Solve system of equations
            - Substitute back to verify
            - Check for non-negative and integer constraints""",
            
            "Multi-entity": """Solve using entity-state tracking.
            - Create table for each entity's quantity
            - Apply operations per entity
            - Track changes and relationships
            - Sum or compare final states
            - Ensure consistency across entities"""
        }

        # Extract problem type
        problem_type = "Comparison"  # default fallback
        for line in problem_analysis.split('\n'):
            if line.startswith("TYPE:"):
                problem_type = line.split(":", 1)[1].strip()
                break

        # Generate 2 solution attempts with type-specific and general instructions
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""{solution_instructions.get(problem_type, solution_instructions['Comparison'])}
                
                Additional constraints from analysis:
                {problem_analysis}
                
                Show ALL work. Box final answer as: \\boxed{{number}}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using alternative mathematical approach.
                
                Problem type: {problem_type}
                Key constraints: {problem_analysis}
                
                If algebraic, try arithmetic. If arithmetic, try algebraic.
                Show complete derivation. Final answer must be numerical.
                Format: Step 1: ... Step 2: ... Final Answer: \\boxed{{number}}""",
                context=""
            )
        )

        # === PHASE 4: CROSS-VALIDATION & CONFLICT RESOLUTION ===
        validation_instruction = """Compare both solution attempts:
        - Do they arrive at the same numerical answer?
        - Are units consistent throughout?
        - Do intermediate steps make logical sense?
        - Are constraints (integer, positive, etc.) respected?
        - Is the final answer plausible in real-world context?
        
        If conflict:
        - Identify exact step where solutions diverge
        - Diagnose cause (misread number, wrong operation, unit error)
        - Select the more consistent solution OR synthesize correct path
        
        If agreement:
        - Extract the numerical answer
        
        Output ONLY the final numerical answer as integer or decimal."""

        validated_answer = await self.ensemble(
            instruction=validation_instruction,
            contexts_list=solution_attempts
        )

        # === PHASE 5: META-VALIDATION & EARLY TERMINATION ===
        # Check if answer is clean number (no text, just digits and decimal)
        number_pattern = r'^[+-]?\d+(\.\d+)?$'
        if not re.match(number_pattern, validated_answer.strip()):
            # Revise with strict extraction
            validated_answer = await self.revise(
                instruction="""Extract ONLY the numerical answer from the text.
                Remove all units, labels, and explanations.
                If multiple numbers, pick the final answer.
                If no clear number, return 0.
                Output must be pure number: integer or decimal.""",
                context=validated_answer
            )

        return validated_answer.strip()