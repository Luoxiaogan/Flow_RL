# Workflow ID: mbppplus_82_0
# Benchmark: mbppplus
# Data Indices: [307, 260]

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

        # Step 1: Initial problem analysis and classification
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Identify:
            1. The primary operation type (search, filter, transform, compute, validate, etc.)
            2. Input and output data types (list, tuple, string, number, etc.)
            3. Key constraints (preserve order, handle duplicates, edge cases like empty inputs)
            4. Whether the problem is atomic (single-step) or composite (multi-step)
            5. Any ambiguity in requirements that needs resolution
            6. Common pitfalls specific to this problem type
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Classify problem complexity to determine routing
        complexity_assessment = await self.generate(
            instruction=f"""Based on the following analysis:
            {problem_analysis}
            
            Classify this problem as either:
            - "ATOMIC": Can be solved with a single, straightforward algorithm (e.g., linear search, simple filter)
            - "COMPOSITE": Requires multiple coordinated steps or complex logic (e.g., string normalization + frequency counting + comparison)
            
            Also identify if there are ambiguous requirements that would benefit from generating multiple solution variants.
            
            Respond with only one of: "ATOMIC", "COMPOSITE_AMBIGUOUS", or "COMPOSITE_CLEAR".""",
            context=problem_analysis
        )

        # Step 3: Route based on complexity
        if "ATOMIC" in complexity_assessment:
            # Direct path for simple problems
            solution_code = await self.programmer(
                instruction=f"""Generate a Python function that solves the problem with the following considerations:
                - Handle all edge cases (empty inputs, single elements, boundary conditions)
                - Match exact return type and function signature
                - Include defensive checks for unexpected inputs
                - Optimize for clarity and efficiency
                - Reference common pitfalls from this analysis: {problem_analysis}
                
                Return only the function implementation with necessary imports, nothing else.""",
                context=problem_analysis,
                max_retries=3
            )
            
        elif "COMPOSITE_AMBIGUOUS" in complexity_assessment:
            # Generate multiple solution variants for ambiguous problems
            variant_instructions = [
                f"""Generate Solution Variant A: Assume strict interpretation of requirements.
                Analysis context: {problem_analysis}""",
                f"""Generate Solution Variant B: Assume lenient interpretation (e.g., ignore case/spaces if applicable).
                Analysis context: {problem_analysis}""",
                f"""Generate Solution Variant C: Most defensive/robust interpretation.
                Analysis context: {problem_analysis}"""
            ]
            
            variants = await asyncio.gather(
                *[self.programmer(
                    instruction=instr,
                    context=problem_analysis,
                    max_retries=2
                ) for instr in variant_instructions]
            )
            
            # Ensemble select the best variant
            solution_code = await self.ensemble(
                instruction="""Select the best solution variant based on:
                1. Completeness in handling edge cases
                2. Adherence to likely problem intent
                3. Code clarity and efficiency
                4. Robustness against unexpected inputs
                Return only the selected code, nothing else.""",
                contexts_list=variants
            )
            
        else:  # COMPOSITE_CLEAR
            # Decompose and solve step by step
            decomposition = await self.decompose(
                instruction=f"""Break down this composite problem into atomic subproblems:
                - Each subproblem should be independently solvable
                - Specify dependencies between subproblems
                - Include data type requirements for inputs/outputs of each step
                - Consider edge cases at each step
                Problem context: {problem_analysis}""",
                context=problem_analysis
            )
            
            # Process subproblems in parallel where possible
            subproblem_solutions = {}
            for subproblem in decomposition:
                sub_id = subproblem['id']
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                
                # Wait for dependencies if any
                if deps and any(dep.strip() in subproblem_solutions for dep in deps if dep.strip()):
                    await asyncio.gather(*[subproblem_solutions[dep.strip()] for dep in deps if dep.strip() in subproblem_solutions])
                
                # Solve subproblem
                solution = await self.programmer(
                    instruction=f"""Solve this subproblem: {subproblem['description']}
                    Context from problem analysis: {problem_analysis}
                    Ensure solution handles edge cases and matches required data types.
                    Return only the code snippet for this subproblem, nothing else.""",
                    context=problem_analysis,
                    max_retries=2
                )
                subproblem_solutions[sub_id] = solution
            
            # Integrate subproblem solutions into final code
            integration_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in subproblem_solutions.items()])
            solution_code = await self.programmer(
                instruction=f"""Integrate these subproblem solutions into a complete function:
                {integration_context}
                
                Ensure:
                - Proper function signature as specified in original problem
                - Seamless data flow between subproblems
                - Comprehensive error handling
                - Final output matches expected type and format
                Return only the complete function implementation with necessary imports, nothing else.""",
                context=integration_context,
                max_retries=3
            )

        # Step 4: Validation and refinement loop
        for iteration in range(3):  # Maximum 3 refinement cycles
            validation_check = await self.generate(
                instruction=f"""Critically review this code for common pitfalls:
                {solution_code}
                
                Check specifically for:
                1. Edge case handling (empty inputs, single elements, boundary values)
                2. Correct return type (list vs tuple vs set, etc.)
                3. Input validation and defensive programming
                4. Efficiency concerns (unnecessary complexity)
                5. Adherence to problem requirements
                6. Code clarity and maintainability
                
                If no issues found, respond with "VALID". Otherwise, list specific issues to fix.""",
                context=solution_code
            )
            
            if "VALID" in validation_check.upper():
                break
            else:
                solution_code = await self.revise(
                    instruction=f"""Revise the code to fix these issues:
                    {validation_check}
                    
                    Maintain the original function signature and core logic while addressing the problems.
                    Return only the revised code, nothing else.""",
                    context=solution_code
                )

        return solution_code