# Workflow ID: mbppplus_162_0
# Benchmark: mbppplus
# Data Indices: [36, 268]

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

        # Phase 1: Problem Fingerprinting - Deep analysis to classify problem type
        fingerprint_instruction = """
        Perform a comprehensive analysis of this programming problem. Classify it along the following dimensions:
        1. ProblemCategory: Choose one - "ScalarLogic", "DataStructure", "Algorithmic", "Hybrid"
        2. InputComplexity: "Simple" (single values) or "Complex" (nested structures, lists, etc.)
        3. OutputType: What type of value is returned? (e.g., "Boolean", "List", "Number", "String")
        4. EdgeCases: List potential edge cases (e.g., empty inputs, single elements, duplicates, boundaries)
        5. SolutionApproach: Suggest the primary solving strategy (e.g., "DirectComparison", "Filtering", "Iteration", "Recursion")
        6. RequiresDecomposition: "Yes" or "No" - does this need to be broken into subproblems?
        7. ValidationFocus: What should be double-checked? (e.g., "TypeConsistency", "BoundaryConditions", "OrderPreservation")
        
        Format your response as a JSON-like dictionary with these exact keys. Be concise but precise.
        Example: {"ProblemCategory": "ScalarLogic", "InputComplexity": "Simple", ...}
        """
        
        fingerprint_raw = await self.generate(instruction=fingerprint_instruction, context="")
        
        try:
            # Extract fingerprint - robust parsing since LLM output may have extra text
            start_idx = fingerprint_raw.find('{')
            end_idx = fingerprint_raw.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                fingerprint_json = fingerprint_raw[start_idx:end_idx]
                fingerprint = json.loads(fingerprint_json)
            else:
                # Fallback classification if parsing fails
                fingerprint = {
                    "ProblemCategory": "ScalarLogic",
                    "InputComplexity": "Simple",
                    "OutputType": "Boolean",
                    "EdgeCases": ["empty inputs"],
                    "SolutionApproach": "DirectComparison",
                    "RequiresDecomposition": "No",
                    "ValidationFocus": "TypeConsistency"
                }
        except:
            fingerprint = {
                "ProblemCategory": "ScalarLogic",
                "InputComplexity": "Simple",
                "OutputType": "Boolean",
                "EdgeCases": ["empty inputs"],
                "SolutionApproach": "DirectComparison",
                "RequiresDecomposition": "No",
                "ValidationFocus": "TypeConsistency"
            }

        # Phase 2: Dynamic Pathway Selection
        solution_code = ""
        
        if fingerprint["ProblemCategory"] == "ScalarLogic" and fingerprint["RequiresDecomposition"] == "No":
            # Path A: Simple direct solution
            programmer_instruction = f"""
            Generate a Python function that solves this problem directly.
            Problem characteristics: {json.dumps(fingerprint, indent=2)}
            
            Requirements:
            - Handle all edge cases mentioned: {', '.join(fingerprint.get('EdgeCases', []))}
            - Return correct type: {fingerprint.get('OutputType', 'appropriate type')}
            - Use minimal, efficient code
            - Include necessary imports at top of function if any
            - Function signature must match exactly what's implied by the problem
            
            Generate ONLY the function implementation as specified in the requirements.
            """
            
            solution_code = await self.programmer(instruction=programmer_instruction, context="", max_retries=3)
            
        elif fingerprint["ProblemCategory"] in ["DataStructure", "Algorithmic", "Hybrid"]:
            # Path B/C/D: Complex problems requiring decomposition or parallel approaches
            
            if fingerprint["RequiresDecomposition"] == "Yes":
                # Decompose into subproblems
                decompose_instruction = f"""
                Break this problem down into essential subproblems. Each subproblem should be:
                - Independently solvable
                - Clearly defined with inputs and expected outputs
                - Ordered by dependency (if any)
                - Focused on one aspect (e.g., "validate input", "transform data", "apply filter")
                
                Problem context: {json.dumps(fingerprint, indent=2)}
                
                Return a list of subproblems with 'id', 'description', and 'dependencies'.
                """
                
                subproblems = await self.decompose(instruction=decompose_instruction, context="")
                
                # Solve subproblems - simple sequential approach for now
                solutions = []
                for sp in subproblems:
                    sp_instruction = f"""
                    Solve this subproblem: {sp['description']}
                    Context: {json.dumps(fingerprint, indent=2)}
                    Dependencies (already solved): {', '.join(solutions[-1:]) if solutions else 'None'}
                    
                    Generate code or pseudocode that solves JUST this subproblem.
                    """
                    sp_solution = await self.generate(instruction=sp_instruction, context=json.dumps(solutions[-1:]) if solutions else "")
                    solutions.append(sp_solution)
                
                # Ensemble final solution from subproblem solutions
                ensemble_instruction = f"""
                Synthesize a complete solution from these subproblem solutions:
                {json.dumps(solutions, indent=2)}
                
                Problem fingerprint: {json.dumps(fingerprint, indent=2)}
                
                Generate a complete, runnable Python function that integrates all subproblem solutions.
                Ensure proper handling of edge cases and return types.
                """
                
                solution_code = await self.ensemble(instruction=ensemble_instruction, contexts_list=solutions)
                
            else:
                # Parallel generate approaches then ensemble
                approach_instructions = [
                    f"Solve using a {fingerprint['SolutionApproach']} approach. Focus on {fingerprint['ValidationFocus']}.",
                    "Solve using the most straightforward, readable approach possible.",
                    "Solve with maximum efficiency and minimal code."
                ]
                
                parallel_solutions = await asyncio.gather(
                    *[self.generate(instruction=f"Problem: {self.problem_text}\n\n{instr}\n\nGenerate complete function code.", context="") 
                      for instr in approach_instructions]
                )
                
                solution_code = await self.ensemble(
                    instruction=f"""
                    Select the best solution from these candidates. Criteria:
                    1. Correctness (must handle edge cases: {', '.join(fingerprint.get('EdgeCases', []))})
                    2. Type consistency (return {fingerprint.get('OutputType', 'appropriate type')})
                    3. Readability and simplicity
                    4. Efficiency
                    
                    Problem fingerprint: {json.dumps(fingerprint, indent=2)}
                    """,
                    contexts_list=parallel_solutions
                )
        
        # Phase 3: Validation and Refinement
        validation_instruction = f"""
        Critically review this solution for the following:
        1. Does it handle ALL edge cases? {', '.join(fingerprint.get('EdgeCases', []))}
        2. Does it return the correct type? {fingerprint.get('OutputType', 'appropriate type')}
        3. Is the code robust against invalid inputs?
        4. Are there any off-by-one errors or boundary issues?
        5. Does it match the expected function signature?
        
        If any issues are found, revise the code to fix them.
        If no issues, return the code unchanged.
        
        Current solution:
        {solution_code}
        """
        
        refined_code = await self.revise(instruction=validation_instruction, context=solution_code)
        
        # Final cleanup - ensure code is minimal and matches requirements
        cleanup_instruction = """
        Return ONLY the final function implementation as specified in the original requirements.
        Remove any explanatory text, markdown, or additional commentary.
        Ensure imports are included if needed.
        The output should be ready to execute as Python code.
        """
        
        final_code = await self.summarize(instruction=cleanup_instruction, context=refined_code)
        
        return final_code