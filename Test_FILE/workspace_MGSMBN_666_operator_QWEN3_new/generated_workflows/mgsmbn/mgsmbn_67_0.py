# Workflow ID: mgsmbn_67_0
# Benchmark: mgsmbn
# Data Indices: [199, 189]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Perform deep problem classification for Bengali math word problems. Analyze:
            1. Problem Type: Sequential, Proportional, Distribution, Comparison, or Multi-entity
            2. Key Entities: Identify all people/objects and their relationships
            3. Temporal Structure: Single event or multi-day/step progression?
            4. Unit Requirements: Are unit conversions needed? (calories, pizzas, etc.)
            5. Hidden Steps: Are there unstated intermediate calculations?
            6. Constraint Flags: Any real-world constraints? (no negative items, whole numbers only, etc.)
            7. Mathematical Operations: Primary operations needed (addition, multiplication, percentages, etc.)
            Output as structured JSON with keys: type, entities, temporal, units, hidden_steps, constraints, operations""",
            context=""
        )

        # PHASE 2: PARALLEL ANALYSIS BRANCHES (DIAMOND PATTERN)
        entity_analysis_task = self.generate(
            instruction=f"""Based on classification: {classification}
            Perform detailed entity tracking:
            - List all named entities with their attributes
            - Map relationships between entities (who has more, who depends on whom)
            - Track changes across time if applicable
            - Resolve any ambiguous pronouns or references
            Output as clear, structured text suitable for computational modeling.""",
            context=""
        )

        math_modeling_task = self.generate(
            instruction=f"""Based on classification: {classification}
            Develop mathematical model:
            - Extract all numerical values and their meanings
            - Define variables for unknowns
            - Write equations or relationships connecting values
            - Identify order of operations
            - Flag any proportional or percentage relationships
            Output as step-by-step mathematical framework with clear variable definitions.""",
            context=""
        )

        unit_constraint_task = self.generate(
            instruction=f"""Based on classification: {classification}
            Analyze units and constraints:
            - List all units mentioned and their conversions if needed
            - Identify final answer unit requirements
            - Note any real-world constraints (must be integer, non-negative, etc.)
            - Flag any potential unit inconsistency risks
            Output as bullet-point list of unit rules and constraints.""",
            context=""
        )

        # Execute parallel branches
        entity_analysis, math_modeling, unit_constraint = await asyncio.gather(
            entity_analysis_task, math_modeling_task, unit_constraint_task
        )

        # PHASE 3: CONTEXT WEAVING - CREATE RICH COMPUTATIONAL CONTEXT
        woven_context = f"""COMPREHENSIVE PROBLEM ANALYSIS:
        === CLASSIFICATION ===
        {classification}

        === ENTITY ANALYSIS ===
        {entity_analysis}

        === MATHEMATICAL MODEL ===
        {math_modeling}

        === UNIT & CONSTRAINTS ===
        {unit_constraint}

        Based on this comprehensive analysis, generate precise Python code to solve the problem.
        """

        # PHASE 4: COMPUTATIONAL SOLUTION WITH VALIDATION LOOP
        solution = None
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Generate and execute code
                code_result = await self.programmer(
                    instruction=f"""Generate Python code that solves the problem using this comprehensive analysis:
                    {woven_context}
                    
                    Requirements:
                    - Use clear variable names matching entity analysis
                    - Follow mathematical model exactly
                    - Apply unit conversions as specified
                    - Respect all constraints (non-negative, integer if required)
                    - Output ONLY the final numerical answer (no text, no units)
                    - Include error handling for edge cases
                    - Double-check all calculations
                    """,
                    context=woven_context,
                    max_retries=1
                )
                
                # Extract numerical answer from code result
                solution = self._extract_number(code_result)
                
                # Validate solution
                validation = await self.generate(
                    instruction=f"""Validate this solution: {solution}
                    Against original problem and constraints:
                    - Does it match expected unit?
                    - Is it within real-world constraints?
                    - Does it satisfy all relationships in mathematical model?
                    - Is the magnitude reasonable?
                    Respond ONLY with 'VALID' if acceptable, or detailed error description if not.""",
                    context=woven_context
                )
                
                if "VALID" in validation.upper():
                    break
                else:
                    # Revise with error feedback
                    woven_context = await self.revise(
                        instruction=f"""Revise the analysis based on this validation error: {validation}
                        - Correct any misidentified relationships
                        - Fix mathematical model if flawed
                        - Adjust unit handling if needed
                        - Strengthen constraint checking
                        Maintain all correct parts of previous analysis.""",
                        context=woven_context
                    )
                    
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise Exception(f"Failed after {max_attempts} attempts: {str(e)}")
                continue

        return solution

    def _extract_number(self, text):
        """Extract numerical answer from text"""
        import re
        # Look for numbers, including those with commas and decimals
        numbers = re.findall(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', text)
        if numbers:
            # Clean commas and convert to float/int
            cleaned = numbers[0].replace(',', '')
            if '.' in cleaned:
                return float(cleaned)
            else:
                return int(cleaned)
        raise ValueError(f"No number found in: {text}")