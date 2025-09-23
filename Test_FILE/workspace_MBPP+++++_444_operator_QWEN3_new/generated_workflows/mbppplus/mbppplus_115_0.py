# Workflow ID: mbppplus_115_0
# Benchmark: mbppplus
# Data Indices: [299, 271, 84]

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
        import json

        # PHASE 1: PARALLEL PROBLEM ANALYSIS (Diamond Fork)
        classification, edge_case_brainstorm = await asyncio.gather(
            self.generate(
                instruction="""Perform deep problem classification. Analyze:
                1. Primary domain: Is this string manipulation, set/list operations, number theory, or logic?
                2. Key operations: What core algorithmic primitive is needed? (e.g., regex matching, subset testing, prime generation)
                3. Input types: What data types are involved? (strings, lists, numbers, nested structures)
                4. Output requirements: What must be returned? (boolean, number, list, etc.)
                5. Hidden constraints: What edge cases or implicit rules might exist?
                6. Confidence level: How certain are you of this classification? (High/Medium/Low)
                Format as JSON with keys: domain, operations, input_types, output_type, constraints, confidence""",
                context=""
            ),
            self.generate(
                instruction="""Brainstorm potential edge cases and failure modes. Consider:
                - Empty inputs (empty string, empty list, n=0)
                - Single-element cases
                - Boundary values (min/max, first/last)
                - Type mismatches or unexpected nesting
                - Duplicates vs unique elements
                - Performance constraints (large inputs)
                - Special values (negative numbers, zero, None)
                Return as bullet-point list, one edge case per line, with brief rationale""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE VALIDATION CRITERIA (Diamond Merge)
        validation_criteria = await self.ensemble(
            instruction="""Synthesize a comprehensive validation checklist from edge case brainstorm.
            1. Extract all unique edge cases
            2. Prioritize by likelihood and severity
            3. Add validation steps to catch each case
            4. Include type checking and boundary condition tests
            5. Format as numbered list of validation rules
            6. Add one meta-rule: "Solution must match reference signature exactly"
            Output ONLY the numbered validation checklist""",
            contexts_list=[edge_case_brainstorm]
        )

        # PHASE 3: CONDITIONAL SOLUTION STRATEGY (Branch based on classification)
        classification_data = json.loads(classification)
        domain = classification_data.get('domain', '').lower()
        
        if 'string' in domain or 'pattern' in domain:
            solution_context = await self.generate(
                instruction=f"""Generate solution for string/pattern problem.
                Classification: {classification}
                Validation Criteria: {validation_criteria}
                
                Requirements:
                - Use regex if pattern matching is involved
                - Handle empty string edge case
                - Consider case sensitivity unless specified otherwise
                - Return exact type specified (usually boolean)
                - Match reference function signature exactly
                - Include necessary imports (re) inside function if needed
                Output ONLY the function implementation, no explanations""",
                context=""
            )
        elif 'set' in domain or 'list' in domain or 'subset' in domain:
            solution_context = await self.generate(
                instruction=f"""Generate solution for set/list containment problem.
                Classification: {classification}
                Validation Criteria: {validation_criteria}
                
                Critical considerations:
                - Handle nested structures (lists within lists)
                - Distinguish between value equality and object identity
                - Empty list edge cases
                - Duplicates in collections
                - Order preservation requirements
                - Return type must match exactly (boolean, list, etc.)
                - Match reference function signature exactly
                Output ONLY the function implementation, no explanations""",
                context=""
            )
        elif 'number' in domain or 'prime' in domain or 'math' in domain:
            solution_context = await self.generate(
                instruction=f"""Generate solution for number theory/mathematical problem.
                Classification: {classification}
                Validation Criteria: {validation_criteria}
                
                Requirements:
                - Handle n<2 edge cases for prime problems
                - Consider efficiency for large inputs
                - Use sieve methods when appropriate
                - Validate mathematical correctness
                - Return exact numeric type specified
                - Match reference function signature exactly
                Output ONLY the function implementation, no explanations""",
                context=""
            )
        else:
            # Default comprehensive approach
            solution_context = await self.generate(
                instruction=f"""Generate solution using general problem-solving framework.
                Classification: {classification}
                Validation Criteria: {validation_criteria}
                
                Requirements:
                - Analyze input/output types carefully
                - Handle all edge cases from validation criteria
                - Choose most appropriate algorithmic approach
                - Ensure type consistency and boundary handling
                - Match reference function signature exactly
                Output ONLY the function implementation, no explanations""",
                context=""
            )

        # PHASE 4: ITERATIVE REFINEMENT (Revise against validation criteria)
        for iteration in range(2):  # Maximum 2 refinement iterations
            revised_solution = await self.revise(
                instruction=f"""Critically revise this solution:
                1. Check against ALL validation criteria: {validation_criteria}
                2. Verify edge case handling (empty inputs, boundaries, etc.)
                3. Ensure type correctness and function signature match
                4. Improve efficiency if possible without sacrificing correctness
                5. Fix any logical errors or oversights
                6. Maintain clean, readable code
                Output ONLY the revised function implementation, no explanations""",
                context=solution_context
            )
            
            # Only update if revision made substantive changes
            if revised_solution.strip() != solution_context.strip():
                solution_context = revised_solution
            else:
                break  # No changes needed, exit early

        return solution_context