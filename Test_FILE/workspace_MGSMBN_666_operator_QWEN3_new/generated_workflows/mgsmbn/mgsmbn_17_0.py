# Workflow ID: mgsmbn_17_0
# Benchmark: mgsmbn
# Data Indices: [55]

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

        # STEP 1: Decompose the problem into structured subproblems and relationships
        decomposition = await self.decompose(
            instruction="""Break down this Bengali math word problem into atomic, solvable components. For each component:
            - Identify the entities (people, objects, units)
            - Extract all numerical values and their semantic roles (price, quantity, rate, etc.)
            - Determine mathematical operations required (add, multiply, round, etc.)
            - Note dependencies between steps (e.g., "first calculate X, then use it in Y")
            - Flag any implicit constraints (e.g., "nearest whole number", "no fractions of people")
            - Preserve Bengali terminology but map to mathematical concepts
            Output as structured subproblems with clear dependencies.""",
            context=""
        )

        # STEP 2: Generate multiple parallel interpretations of the problem
        interpretation_tasks = [
            self.generate(
                instruction=f"""Interpret this problem from a UNIT ECONOMICS perspective:
                - Focus on per-unit calculations (price per item, cost per hour, etc.)
                - Explicitly model how individual transactions contribute to the total
                - Highlight any rounding or approximation rules applied at the unit level
                - Ignore global totals until the final step
                Base your reasoning on this decomposition: {json.dumps(decomposition)}""",
                context=""
            ),
            self.generate(
                instruction=f"""Interpret this problem from a TOTAL SUMMATION perspective:
                - Focus on aggregate calculations (total cost, total time, total earnings)
                - Model how components combine into the final answer
                - Highlight any rounding or approximation rules applied at the aggregate level
                - Consider order of operations (e.g., round then sum vs. sum then round)
                Base your reasoning on this decomposition: {json.dumps(decomposition)}""",
                context=""
            ),
            self.generate(
                instruction=f"""Interpret this problem from a CONSTRAINT-BASED perspective:
                - Identify all explicit and implicit constraints (integer values, non-negative, unit consistency)
                - Model how constraints affect the solution path
                - Flag any potential violations or edge cases
                - Suggest conservative assumptions where ambiguity exists
                Base your reasoning on this decomposition: {json.dumps(decomposition)}""",
                context=""
            )
        ]
        
        interpretations = await asyncio.gather(*interpretation_tasks)

        # STEP 3: Synthesize interpretations into a unified, validated problem representation
        synthesized = await self.ensemble(
            instruction="""Synthesize these three interpretations into a single, robust problem representation:
            - Identify consensus elements (all interpretations agree on)
            - Resolve contradictions by referring to original problem phrasing
            - Prioritize interpretations that preserve unit semantics and constraints
            - Explicitly state the solution strategy: step-by-step operations, data types, rounding rules
            - Output as a structured JSON-like plan with: entities, operations, constraints, and execution order""",
            contexts_list=interpretations
        )

        # STEP 4: Generate and execute code based on synthesized plan
        code_result = await self.programmer(
            instruction=f"""Generate Python code to solve this problem based EXACTLY on this synthesized plan:
            {synthesized}
            
            Requirements:
            - Use float for intermediate calculations, int for final rounded values if specified
            - Implement all constraints (e.g., rounding per item, not on total)
            - Include validation checks (no negative quantities, unit consistency)
            - Print only the final numerical answer (no explanations)
            - Handle edge cases gracefully (division by zero, empty inputs)""",
            context=synthesized,
            max_retries=2
        )

        # STEP 5: Validate and iteratively refine if needed
        for attempt in range(2):
            validation = await self.generate(
                instruction=f"""Validate this result against the original problem:
                - Does the numerical answer match the expected scale and units?
                - Were all constraints (rounding, integer values, etc.) properly applied?
                - Is the answer logically consistent with the problem narrative?
                - Flag any discrepancies or potential errors.
                Current result: {code_result}""",
                context=code_result
            )
            
            if "error" not in validation.lower() and "discrepancy" not in validation.lower() and "incorrect" not in validation.lower():
                break
                
            # Revise and retry
            code_result = await self.revise(
                instruction=f"""Fix the code based on this validation feedback:
                {validation}
                
                Requirements:
                - Preserve correct parts of the previous solution
                - Address all flagged issues
                - Maintain unit and constraint consistency
                - Output only the corrected code and result""",
                context=code_result
            )

        # STEP 6: Extract final numerical answer (clean output)
        final_answer = await self.generate(
            instruction="""Extract ONLY the final numerical answer from this result. 
            - If multiple numbers appear, select the one that answers the original question
            - Remove any units, explanations, or formatting
            - Output as a plain integer or decimal number
            - If no clear answer, return 0 as fallback""",
            context=code_result
        )

        return final_answer.strip()