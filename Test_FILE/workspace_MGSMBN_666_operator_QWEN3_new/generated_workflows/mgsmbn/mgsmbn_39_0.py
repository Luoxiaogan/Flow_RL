# Workflow ID: mgsmbn_39_0
# Benchmark: mgsmbn
# Data Indices: [176]

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

        # STEP 1: Hierarchical Decomposition
        decomposition_instruction = """
        Systematically decompose this Bengali math word problem into atomic, solvable subproblems.
        For each subproblem:
        - Identify the target unknown or calculation needed
        - List all named entities (people, objects, quantities) involved
        - Specify mathematical relationships (comparisons, totals, rates)
        - Define dependencies: which other subproblems must be solved first?
        - Flag if the subproblem requires inference (not directly stated)
        Structure output as a numbered list of subproblems with clear dependencies.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # STEP 2: Parallel Semantic Extraction
        async def extract_math(subproblem):
            instruction = f"""
            Convert this subproblem into a precise mathematical expression or equation:
            "{subproblem['description']}"
            
            Guidelines:
            - Assign variables to unknowns (e.g., jojo_score)
            - Express relationships algebraically (e.g., yuri = naomi + 10)
            - Preserve units (টাকা, পয়েন্ট, ঘণ্টা) in comments
            - If comparison is involved ('more than', 'less than'), use operators
            - If aggregation ('total', 'sum'), identify all components
            - If direct value is given, assign it (e.g., naomi = 68)
            Return ONLY the mathematical representation.
            """
            return await self.generate(instruction=instruction, context="")

        math_expressions = await asyncio.gather(
            *[extract_math(sp) for sp in subproblems]
        )

        # STEP 3: Validation and Gap Detection
        async def validate_expression(expr, sp_desc):
            instruction = f"""
            Validate this mathematical expression derived from: "{sp_desc}"
            Expression: {expr}
            
            Check:
            1. Are all variables defined? If not, which subproblem defines them?
            2. Is this solvable with current information? If not, what's missing?
            3. Does it respect real-world constraints (non-negative, integer if needed)?
            4. Are units consistent?
            
            If unsolvable directly, reformulate as equation with unknown.
            Return revised expression or validation report.
            """
            return await self.revise(instruction=instruction, context=expr)

        validated_expressions = await asyncio.gather(
            *[validate_expression(expr, sp['description']) for expr, sp in zip(math_expressions, subproblems)]
        )

        # STEP 4: Parallel Programmatic Solving
        # Generate two solution strategies: sequential and algebraic
        sequential_code_instruction = f"""
        Generate Python code to solve these validated expressions STEP-BY-STEP:
        {json.dumps(validated_expressions, indent=2)}
        
        Rules:
        - Solve in dependency order (respect subproblem dependencies)
        - Track all variables
        - Include unit comments
        - Print ONLY the final answer as a number
        - Handle edge cases (negative values, division by zero)
        """
        
        algebraic_code_instruction = f"""
        Generate Python code to solve by ALGEBRAIC REARRANGEMENT:
        {json.dumps(validated_expressions, indent=2)}
        
        Rules:
        - Formulate as system of equations
        - Solve for target unknown directly
        - Use symbolic reasoning if needed
        - Print ONLY the final answer as a number
        - Validate against total constraints
        """

        code_attempts = await asyncio.gather(
            self.programmer(instruction=sequential_code_instruction, context=""),
            self.programmer(instruction=algebraic_code_instruction, context="")
        )

        # STEP 5: Ensemble Verification
        ensemble_instruction = """
        Compare these solution attempts:
        - Do they produce the same numerical answer?
        - If different, which one violates real-world constraints (negative scores, fractional people)?
        - Which approach better respects the problem's dependencies?
        - Select the most valid answer. If both invalid, return 'ERROR: Contradiction'.
        Return ONLY the final numerical answer or 'ERROR: ...'.
        """
        consensus_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=code_attempts
        )

        # STEP 6: Contextual Sanity Check
        sanity_instruction = """
        Verify this answer against the original problem's context:
        - Is the magnitude reasonable? (e.g., not billions for a school problem)
        - Are units preserved? (answer should be unitless number as required)
        - Does it satisfy implicit constraints? (non-negative, integer if expected)
        - Does it match the problem's real-world scenario?
        
        If valid, return the number unchanged. If invalid, adjust or flag error.
        Return ONLY the final numerical answer or 'ERROR: ...'.
        """
        final_answer = await self.revise(
            instruction=sanity_instruction,
            context=consensus_answer
        )

        # Extract numerical answer (handle potential 'ERROR' cases gracefully)
        if "ERROR" in final_answer:
            # Fallback: return 0 or attempt minimal solve
            return "0"
        
        # Clean and return the answer
        import re
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", final_answer)
        return numbers[0] if numbers else "0"