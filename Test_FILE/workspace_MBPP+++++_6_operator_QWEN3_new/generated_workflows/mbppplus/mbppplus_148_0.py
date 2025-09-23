# Workflow ID: mbppplus_148_0
# Benchmark: mbppplus
# Data Indices: [362, 142]

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
        import re

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into atomic subproblems. For each subproblem, identify:
            1. The core computational task (e.g., mathematical formula, list manipulation, string parsing)
            2. Required input validation or edge cases (e.g., empty inputs, zero values, boundary conditions)
            3. Expected output structure and data types (e.g., must return tuple, preserve order, handle duplicates)
            4. Any implicit constraints or assumptions
            Return as structured list of subproblems with clear dependencies.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Develop a solution strategy focusing on mathematical/computational efficiency. 
            Derive formulas, identify invariants, and optimize for minimal operations. 
            Consider numerical stability and overflow cases.""",
            
            """Develop a solution strategy focusing on data structure manipulation. 
            Consider list slicing, indexing, set operations, or string methods. 
            Preserve order where required and handle duplicates appropriately.""",
            
            """Develop a solution strategy focusing on edge case robustness. 
            Systematically handle empty inputs, single elements, zeros, negatives, and boundary values. 
            Write defensive code with explicit conditionals."""
        ]

        strategies = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # Step 3: Convert strategies to code candidates
        code_candidates = []
        for i, strategy in enumerate(strategies):
            try:
                code = await self.programmer(
                    instruction=f"""Implement the solution as a Python function matching the exact signature from the problem.
                    Strategy context: {strategy}
                    Decomposition context: {decomposition}
                    
                    Requirements:
                    - Include all necessary imports inside the function if needed
                    - Match exact parameter names and return types
                    - Handle all edge cases identified in decomposition
                    - Return ONLY the function implementation, no wrapper code
                    - Ensure type consistency (list vs tuple vs set)""",
                    context=strategy,
                    max_retries=2
                )
                code_candidates.append(code)
            except Exception as e:
                # Fallback: generate without programmer if it fails
                fallback_code = await self.generate(
                    instruction=f"""Write Python function implementation based on this strategy:
                    {strategy}
                    
                    Must match exact function signature and handle edge cases.
                    Return ONLY the function code, no explanations.""",
                    context=strategy
                )
                code_candidates.append(fallback_code)

        # Step 4: Ensemble select best candidate
        selected_code = await self.ensemble(
            instruction="""Select the best code implementation based on:
            1. Correctness: handles all edge cases from decomposition
            2. Type fidelity: matches expected return types and signatures
            3. Simplicity: minimal, readable, efficient code
            4. Robustness: defensive programming practices
            
            If none are perfect, select the most promising for revision.""",
            contexts_list=code_candidates
        )

        # Step 5: Iterative refinement (up to 3 rounds)
        current_code = selected_code
        for refinement_round in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this code implementation:
                {current_code}
                
                Check for:
                - Signature compliance (exact function name and parameters)
                - Return type correctness (list/tuple/set as required)
                - Edge case handling (empty inputs, zeros, boundaries)
                - Potential bugs or logical errors
                - Missing imports or syntax issues
                
                Return specific, actionable revision instructions if issues found, or 'VALID' if perfect.""",
                context=current_code
            )
            
            if "VALID" in validation_feedback.upper():
                break
                
            # Revise based on feedback
            current_code = await self.revise(
                instruction=f"""Revise the code based on this feedback:
                {validation_feedback}
                
                Requirements:
                - Fix all identified issues
                - Maintain exact function signature
                - Keep code minimal and efficient
                - Return ONLY the function implementation""",
                context=current_code
            )

        # Step 6: Final sanitization - ensure clean output format
        final_code = await self.revise(
            instruction="""Ensure the code output matches EXACT requirements:
            - ONLY the function implementation (no extra text, no markdown)
            - Correct function name and parameters
            - All imports inside function if needed
            - No wrapper classes or additional functions
            - Proper indentation and Python syntax
            
            If any wrapper text exists, strip it out and return only the pure function code.""",
            context=current_code
        )

        # Extract just the function code using regex (in case any explanatory text remains)
        code_pattern = r'(def\s+\w+\s*\(.*?\):.*?)(?=\n\n|\Z)'
        matches = re.findall(code_pattern, final_code, re.DOTALL)
        if matches:
            return matches[0].strip()
        
        return final_code.strip()