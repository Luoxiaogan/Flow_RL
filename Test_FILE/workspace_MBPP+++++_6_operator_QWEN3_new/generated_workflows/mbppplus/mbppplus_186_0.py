# Workflow ID: mbppplus_186_0
# Benchmark: mbppplus
# Data Indices: [167, 37]

import asyncio
import json

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
        
        # Phase 1: Problem Classification
        classification = await self.generate(
            instruction="""Analyze the problem and classify it into one primary type. 
            Available types: ['bitwise', 'mathematical_formula', 'string_manipulation', 'list_algorithm', 'logical_validation', 'data_structure'].
            Provide classification in JSON format with keys:
            - "type": the selected type
            - "confidence": percentage confidence (0-100)
            - "evidence": 2-3 specific clues from problem description or test cases
            - "required_imports": list of Python modules likely needed (e.g., ['math', 'collections'])
            Be conservative in confidence scoring. If uncertain, score below 70.""",
            context=""
        )
        
        try:
            class_data = json.loads(classification)
            problem_type = class_data.get("type", "logical_validation")
            confidence = class_data.get("confidence", 50)
            required_imports = class_data.get("required_imports", [])
        except:
            problem_type = "logical_validation"
            confidence = 50
            required_imports = []
        
        # Phase 2: Strategy Selection (Conditional Branching)
        if confidence >= 70:
            # High confidence: Direct strategy
            strategies = [problem_type]
        else:
            # Low confidence: Parallel exploration
            strategies = ["mathematical_formula", "logical_validation", "bitwise"]
        
        # Phase 3: Parallel Solution Generation
        solution_attempts = []
        for strategy in strategies:
            attempt = await self.generate(
                instruction=f"""Generate a solution strategy for this problem using {strategy} approach.
                Consider:
                - Key operations needed
                - Edge cases to handle (empty inputs, zeros, negatives, boundaries)
                - Required data type conversions
                - Return value format matching test cases
                Output as structured plan with steps.""",
                context=""
            )
            solution_attempts.append(attempt)
        
        # Phase 4: Ensemble Selection
        selected_strategy = await self.ensemble(
            instruction="""Select the best solution strategy from the candidates.
            Criteria:
            1. Best matches problem description and test case patterns
            2. Most comprehensive edge case handling
            3. Cleanest return type alignment
            4. Most efficient approach
            Return only the selected strategy text.""",
            contexts_list=solution_attempts
        )
        
        # Phase 5: Hierarchical Decomposition (if complex)
        decomposition_needed = await self.generate(
            instruction="""Determine if this problem requires decomposition into subproblems.
            Answer 'YES' if problem involves multiple distinct steps or nested operations.
            Answer 'NO' if it's a single straightforward calculation.
            Also identify if order preservation or state management is critical.""",
            context=selected_strategy
        )
        
        if "YES" in decomposition_needed.upper():
            subproblems = await self.decompose(
                instruction="""Break this problem into atomic subproblems.
                Each subproblem should be independently solvable.
                Specify dependencies between subproblems.
                Focus on: input transformation, core computation, output formatting.""",
                context=selected_strategy
            )
            # For simplicity, we'll use the decomposition to inform code generation
            decomposition_context = "\n".join([f"{sp['id']}: {sp['description']}" for sp in subproblems])
        else:
            decomposition_context = "Single-step problem"
        
        # Phase 6: Initial Code Generation
        initial_code = await self.programmer(
            instruction=f"""Generate Python code for this problem.
            Strategy: {selected_strategy}
            Decomposition: {decomposition_context}
            Required imports: {required_imports}
            Critical requirements:
            - Handle all edge cases mentioned in strategy
            - Match exact return type from test cases
            - Include input validation if needed
            - Use efficient algorithms
            - Return only the function implementation (no extra text)""",
            context="",
            max_retries=2
        )
        
        # Phase 7: Edge Case Analysis
        edge_cases = await self.generate(
            instruction="""Identify all possible edge cases for this problem.
            Consider:
            - Empty/None inputs
            - Zero values
            - Negative numbers
            - Maximum/minimum values
            - Duplicate elements
            - Type mismatches
            - Boundary conditions
            For each edge case, specify expected behavior.
            Format as bullet points.""",
            context=selected_strategy
        )
        
        # Phase 8: Code Revision with Edge Cases
        revised_code = await self.revise(
            instruction=f"""Revise the code to handle these edge cases:
            {edge_cases}
            
            Current code:
            {initial_code}
            
            Requirements:
            - Maintain exact function signature
            - Preserve return type consistency
            - Add input validation if missing
            - Optimize for clarity and efficiency
            - Return only the function implementation""",
            context=initial_code
        )
        
        # Phase 9: Type and Format Validation
        final_validation = await self.generate(
            instruction=f"""Verify this code meets all requirements:
            - Function name matches exactly
            - Parameter names match
            - Return type matches test cases (int, bool, list, etc.)
            - Handles all edge cases from: {edge_cases}
            - No unnecessary imports or code
            If any issues found, describe them specifically.
            If perfect, respond with 'VALID'.""",
            context=revised_code
        )
        
        # Phase 10: Final Output
        if "VALID" not in final_validation.upper():
            # One final revision if issues found
            final_code = await self.revise(
                instruction=f"""Fix these issues: {final_validation}
                Current code: {revised_code}
                Return only the corrected function implementation.""",
                context=revised_code
            )
        else:
            final_code = revised_code
        
        return final_code