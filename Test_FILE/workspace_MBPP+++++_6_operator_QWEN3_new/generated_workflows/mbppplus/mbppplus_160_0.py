# Workflow ID: mbppplus_160_0
# Benchmark: mbppplus
# Data Indices: [356, 90]

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
        import re
        
        # Phase 1: Comprehensive Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Identify the core task: What exactly needs to be computed or transformed?
            2. Classify problem type: Mathematical, Structural (data manipulation), String-based, or Logical
            3. Identify input/output data types and structures
            4. Extract key constraints and edge cases (empty inputs, boundaries, special values)
            5. Determine if order preservation is required
            6. Identify potential solution approaches (algorithmic patterns that could apply)
            7. Note any mathematical properties or computational shortcuts that might be relevant
            8. Assess complexity level: Simple (direct calculation), Medium (requires 1-2 steps), Complex (requires decomposition)
            
            Format your analysis as a structured JSON-like response with clear sections.""",
            context=""
        )

        # Phase 2: Problem Classification and Strategy Selection
        classification = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Classify this problem and select primary solution strategy:
            - If mathematical (bit manipulation, number theory, etc.): Choose 'mathematical'
            - If data structure manipulation (grouping, filtering, transforming): Choose 'structural'
            - If string manipulation: Choose 'string'
            - If logical/conditional processing: Choose 'logical'
            
            Also determine:
            - Should we decompose this problem? (Yes for complex multi-step problems, No for simple direct calculations)
            - How many parallel solution approaches should we generate? (1 for simple, 2-3 for complex)
            
            Respond with a simple classification string like: "type: mathematical, decompose: no, parallel: 1" """,
            context=problem_analysis
        )

        # Extract classification decisions
        type_match = re.search(r'type:\s*(\w+)', classification.lower())
        decompose_match = re.search(r'decompose:\s*(yes|no)', classification.lower())
        parallel_match = re.search(r'parallel:\s*(\d+)', classification.lower())
        
        problem_type = type_match.group(1) if type_match else "structural"
        should_decompose = decompose_match.group(1) == "yes" if decompose_match else False
        parallel_count = int(parallel_match.group(1)) if parallel_match else 1

        # Phase 3: Generate solution approaches (parallel if needed)
        if parallel_count > 1:
            # Generate multiple solution approaches in parallel
            solution_instructions = []
            
            if problem_type == "mathematical":
                solution_instructions = [
                    "Solve using bit manipulation and mathematical properties",
                    "Solve using iterative checking and arithmetic operations",
                    "Solve using logarithmic or exponential approaches"
                ]
            elif problem_type == "structural":
                solution_instructions = [
                    "Solve using dictionary/grouping with iteration",
                    "Solve using functional programming approaches (map/filter/reduce)",
                    "Solve using sorting and grouping techniques"
                ]
            elif problem_type == "string":
                solution_instructions = [
                    "Solve using string methods and iteration",
                    "Solve using regular expressions",
                    "Solve using character-by-character processing"
                ]
            else:  # logical or default
                solution_instructions = [
                    "Solve using direct conditional logic",
                    "Solve using state machines or flag-based approaches",
                    "Solve using mathematical modeling of logical conditions"
                ]
            
            # Limit to requested parallel count
            solution_instructions = solution_instructions[:parallel_count]
            
            # Generate solutions in parallel
            solution_attempts = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""Implement a solution for this problem:
                    {instr}
                    
                    Requirements:
                    - Handle all edge cases identified in analysis
                    - Match exact function signature from problem
                    - Include necessary imports
                    - Return correct data type
                    - Code must be clean, efficient, and readable
                    
                    Problem context:
                    {problem_analysis}""",
                    context=problem_analysis
                ) for instr in solution_instructions]
            )
            
            # Use ensemble to select best solution
            final_solution = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Correctness (handles all edge cases)
                2. Efficiency (time and space complexity)
                3. Code clarity and readability
                4. Adherence to problem requirements
                5. Robustness (handles unexpected inputs gracefully)
                
                If multiple solutions are equally good, synthesize the best elements from each.
                Return only the final code implementation, nothing else.""",
                contexts_list=solution_attempts
            )
        else:
            # Single solution approach
            if problem_type == "mathematical":
                solution_instruction = "Solve using the most appropriate mathematical approach (bit manipulation, logarithmic, arithmetic, etc.)"
            elif problem_type == "structural":
                solution_instruction = "Solve using the most appropriate data structure manipulation approach (dictionary, list comprehension, functional programming, etc.)"
            elif problem_type == "string":
                solution_instruction = "Solve using the most appropriate string manipulation approach"
            else:
                solution_instruction = "Solve using the most appropriate logical/conditional approach"
            
            final_solution = await self.programmer(
                instruction=f"""Implement a solution for this problem:
                {solution_instruction}
                
                Requirements:
                - Handle all edge cases identified in analysis
                - Match exact function signature from problem
                - Include necessary imports
                - Return correct data type
                - Code must be clean, efficient, and readable
                
                Problem context:
                {problem_analysis}""",
                context=problem_analysis
            )

        # Phase 4: Iterative refinement (up to 3 iterations)
        current_solution = final_solution
        for i in range(3):
            validation = await self.generate(
                instruction=f"""Critically review this solution:
                {current_solution}
                
                Check for:
                1. Edge case handling (empty inputs, single elements, boundaries, etc.)
                2. Correct return type and function signature
                3. Efficiency concerns
                4. Potential bugs or logical errors
                5. Readability and code quality
                6. Adherence to problem requirements
                
                If any issues are found, provide specific revision instructions.
                If no issues, respond with 'VALID: No revisions needed'.""",
                context=current_solution
            )
            
            if "VALID" in validation and "No revisions needed" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution based on this feedback:
                    {validation}
                    
                    Requirements:
                    - Fix all identified issues
                    - Maintain correct function signature
                    - Keep code clean and readable
                    - Ensure all edge cases are handled
                    
                    Original problem context:
                    {problem_analysis}""",
                    context=current_solution
                )

        # Phase 5: Final code extraction and formatting
        final_code = await self.generate(
            instruction="""Extract only the Python function implementation from the solution.
            Requirements:
            - Include only the function definition and necessary imports
            - Remove any explanatory text, comments (unless critical), or markdown formatting
            - Ensure function signature exactly matches the problem requirements
            - Imports must be at the top of the code block
            - Return statement must be present and correct
            - Code must be properly indented and formatted
            
            If the solution contains multiple code blocks, select the final/improved version.""",
            context=current_solution
        )

        return final_code