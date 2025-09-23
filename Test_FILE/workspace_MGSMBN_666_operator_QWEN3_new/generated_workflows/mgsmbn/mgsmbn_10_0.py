# Workflow ID: mgsmbn_10_0
# Benchmark: mgsmbn
# Data Indices: [122, 161]

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
        import re

        # Step 1: Decompose the problem into subproblems with dependencies
        decomposition = await self.decompose(
            instruction="""Break down this Bengali math word problem into atomic subproblems.
            For each subproblem:
            - Identify what needs to be calculated or inferred
            - Specify dependencies (which other subproblems must be solved first)
            - Label whether it involves: proportional reasoning, unit conversion, temporal logic, distribution, or comparison
            - Flag any implicit constraints (e.g., integer-only answers, non-negative quantities)
            Return as structured list with 'id', 'description', 'dependencies', and 'type' fields.""",
            context=""
        )

        # Step 2: Parallel analysis from three perspectives
        math_perspective = await self.generate(
            instruction="""Adopt a mathematical modeling perspective.
            - Extract all numerical values and assign variables
            - Translate relationships into equations or inequalities
            - Identify the target variable to solve for
            - Show step-by-step algebraic reasoning
            - Output in structured JSON format: {"variables": {}, "equations": [], "solution_path": []}""",
            context=""
        )

        linguistic_perspective = await self.generate(
            instruction="""Adopt a linguistic parsing perspective.
            - Identify all entities (people, objects, quantities)
            - Extract action verbs and their mathematical implications (e.g., 'বেশি' = more → addition, 'গুণ' = times → multiplication)
            - Map Bengali phrases to mathematical operations
            - Highlight ambiguous phrases that need disambiguation
            - Output as structured list: [{"entity": "", "operation": "", "target": ""}]""",
            context=""
        )

        unit_perspective = await self.generate(
            instruction="""Adopt a unit and dimension tracking perspective.
            - Identify all units mentioned (টাকা, জন, ঘণ্টা, etc.)
            - Verify unit consistency across operations
            - Flag any unit conversions needed
            - Ensure final answer unit matches expected output
            - Output as: {"units_found": [], "conversions_needed": [], "consistency_check": "pass/fail", "final_unit": ""}""",
            context=""
        )

        # Step 3: Ensemble synthesis with adversarial validation
        synthesized_approach = await self.ensemble(
            instruction="""You are a mathematical tribunal. Three experts have analyzed the problem:
            - Mathematician: Focused on equations and variables
            - Linguist: Focused on verb semantics and entity relationships
            - Unit Analyst: Focused on dimensional consistency
            
            Your task:
            1. Cross-examine their analyses for contradictions
            2. Resolve ambiguities by prioritizing mathematical consistency
            3. Generate a unified solution plan with explicit steps
            4. Flag any remaining uncertainties
            5. Output as numbered steps with justifications""",
            contexts_list=[math_perspective, linguistic_perspective, unit_perspective]
        )

        # Step 4: Iterative code generation with validation
        final_answer = None
        code_attempts = []
        
        for attempt in range(3):
            try:
                code_result = await self.programmer(
                    instruction=f"""Generate Python code to solve the problem based on this unified plan:
                    {synthesized_approach}
                    
                    Requirements:
                    - Use exact arithmetic (no floating point unless necessary)
                    - Validate intermediate results (no negative people, fractional friends unless specified)
                    - Print only the final numerical answer
                    - Include comments mapping code steps to plan steps""",
                    context=synthesized_approach,
                    max_retries=1
                )
                
                # Extract numerical answer from code output
                match = re.search(r'(\d+(?:\.\d+)?)', code_result)
                if match:
                    candidate_answer = float(match.group(1))
                    # Validate plausibility (e.g., no negative counts)
                    if candidate_answer >= 0:
                        final_answer = candidate_answer
                        break
                    else:
                        raise ValueError("Negative answer not plausible")
                else:
                    raise ValueError("No numerical answer found in code output")
                    
            except Exception as e:
                code_attempts.append(f"Attempt {attempt + 1} failed: {str(e)}")
                # Revise approach based on error
                synthesized_approach = await self.revise(
                    instruction=f"""Previous code attempt failed with error: {str(e)}
                    Revise the solution plan:
                    - Add explicit validation steps
                    - Break down complex operations
                    - Ensure all variables are properly initialized
                    - Double-check unit conversions""",
                    context=synthesized_approach
                )

        # Step 5: Reverse validation (if answer found)
        if final_answer is not None:
            reverse_check = await self.generate(
                instruction=f"""Perform reverse validation:
                Given the answer {final_answer}, reconstruct the problem's initial conditions.
                Verify that all given values (e.g., Charlie's 12 friends, $5000 bonus) are consistent with this answer.
                If any inconsistency, flag it. Otherwise, confirm validity.""",
                context=f"Original approach: {synthesized_approach}"
            )
            
            if "inconsistent" in reverse_check.lower() or "error" in reverse_check.lower():
                # Trigger debug mode
                debug_approach = await self.revise(
                    instruction="""DEBUG MODE: The reverse validation failed.
                    - List all intermediate variables and their expected values
                    - Verify each calculation step by step
                    - Output as explicit variable assignments and checks""",
                    context=synthesized_approach
                )
                
                debug_code = await self.programmer(
                    instruction=f"""Generate debug code with explicit intermediate prints:
                    {debug_approach}
                    Print each intermediate value for verification.""",
                    context=debug_approach
                )
                
                # Extract final answer again from debug code
                match = re.search(r'final answer[:\s]*(\d+(?:\.\d+)?)', debug_code, re.IGNORECASE)
                if match:
                    final_answer = float(match.group(1))

        # Ensure integer output if context implies whole numbers (e.g., people, items)
        if final_answer is not None:
            # Check if problem likely expects integer (e.g., contains 'জন', 'টি')
            if 'জন' in self.problem_text or 'টি' in self.problem_text:
                final_answer = int(round(final_answer))

        return str(final_answer) if final_answer is not None else "0"