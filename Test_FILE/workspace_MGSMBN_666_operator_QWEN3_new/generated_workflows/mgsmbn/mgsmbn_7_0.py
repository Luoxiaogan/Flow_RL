# Workflow ID: mgsmbn_7_0
# Benchmark: mgsmbn
# Data Indices: [159, 74]

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

        # PHASE 1: META-COGNITIVE CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this Bengali math word problem. Answer these questions:
            1. What is the core mathematical genre? (Sequential, Proportional, Distribution, Comparison, Multi-entity, Rate)
            2. How many distinct reasoning steps are required? (1, 2, 3+)
            3. Are there hidden intermediate calculations not explicitly stated?
            4. What are the key entities (people, objects, quantities) and their relationships?
            5. Are there unit consistency requirements or conversions needed?
            6. Are there real-world constraints that must be enforced? (e.g., no negative people, integer outputs)
            7. Is the solution path linear or does it require branching/conditional logic?
            8. What is the expected answer format? (integer, decimal, with/without units)
            
            Format your response as a structured JSON-like analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: CONDITIONAL BRANCHING BASED ON COMPLEXITY
        complexity_check = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Classify complexity level:
            - SIMPLE: Single-step, direct calculation, no hidden steps
            - MODERATE: 2-3 steps, may require decomposition but no branching
            - COMPLEX: Multiple entities, hidden steps, or conditional logic required
            
            Respond with only one word: SIMPLE, MODERATE, or COMPLEX""",
            context=problem_analysis
        )

        if "SIMPLE" in complexity_check.upper():
            # Direct computational path
            solution_attempt = await self.programmer(
                instruction=f"""Solve this Bengali math problem directly:
                {problem_analysis}
                
                Write Python code that:
                1. Extracts all given numerical values and relationships
                2. Performs the required calculation in one step
                3. Outputs only the final numerical answer
                4. Includes assertions for real-world constraints (non-negative, integer if required)
                
                Return only the code and its output.""",
                context=problem_analysis
            )
            final_answer = solution_attempt

        elif "MODERATE" in complexity_check.upper():
            # Decompose into subproblems
            decomposition = await self.decompose(
                instruction=f"""Break this problem into minimal necessary subproblems:
                {problem_analysis}
                
                Requirements:
                - Each subproblem should be solvable independently or with specified dependencies
                - Include ALL intermediate steps, even if not explicitly stated
                - Maintain unit consistency across subproblems
                - Enforce real-world constraints at each step
                - Order subproblems by dependency (prerequisites first)""",
                context=problem_analysis
            )

            # Solve subproblems in parallel where possible
            async def solve_subproblem(sub):
                return await self.programmer(
                    instruction=f"""Solve this subproblem from a Bengali math word problem:
                    Subproblem: {sub['description']}
                    Dependencies: {sub.get('dependencies', 'None')}
                    Context: {problem_analysis}
                    
                    Write Python code that:
                    1. Uses only the information from this subproblem and its dependencies
                    2. Outputs the result in the required format
                    3. Includes validation assertions
                    4. Returns only the numerical result""",
                    context=json.dumps(sub)
                )

            # Group subproblems by dependency level for parallel execution
            solved_results = {}
            max_dependency_depth = max([len(sub.get('dependencies', '').split(',')) if sub.get('dependencies') else 0 for sub in decomposition])
            
            for depth in range(max_dependency_depth + 1):
                current_level_subs = [sub for sub in decomposition if len(sub.get('dependencies', '').split(',')) == depth]
                if not current_level_subs:
                    continue
                    
                # Solve current level in parallel
                tasks = [solve_subproblem(sub) for sub in current_level_subs]
                results = await asyncio.gather(*tasks)
                
                # Store results by subproblem ID
                for i, sub in enumerate(current_level_subs):
                    solved_results[sub['id']] = results[i]

            # Synthesize final answer from last subproblem
            final_sub = decomposition[-1]
            final_answer = solved_results.get(final_sub['id'], "ERROR: Final subproblem not solved")

        else:  # COMPLEX
            # Generate multiple solution paths in parallel
            solution_paths = await asyncio.gather(
                self.generate(
                    instruction=f"""Solution Path 1 (Algebraic):
                    {problem_analysis}
                    
                    Model this as an algebraic equation system.
                    Define variables for unknowns.
                    Write equations based on relationships.
                    Solve step by step.
                    Show all work and final numerical answer.""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""Solution Path 2 (Arithmetic Step-by-Step):
                    {problem_analysis}
                    
                    Solve using only arithmetic operations in logical sequence.
                    Break into smallest possible steps.
                    Show intermediate calculations.
                    Verify each step against constraints.
                    Final answer must be numerical.""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""Solution Path 3 (Unit Analysis & Proportional Reasoning):
                    {problem_analysis}
                    
                    Focus on unit consistency and proportional relationships.
                    Convert all quantities to common units if needed.
                    Use ratio and proportion methods.
                    Track units through each calculation.
                    Final answer with appropriate precision.""",
                    context=problem_analysis
                )
            )

            # Validate each solution path
            validations = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Adversarial Validation: Assume this solution is wrong.
                    Solution: {sol}
                    Problem Analysis: {problem_analysis}
                    
                    Find the most likely error in:
                    - Mathematical reasoning
                    - Unit handling
                    - Constraint violation
                    - Arithmetic calculation
                    - Interpretation of Bengali text
                    
                    If no error found, state "VALID".
                    Otherwise, describe error concisely.""",
                    context=sol
                ) for sol in solution_paths]
            )

            # Revise solutions that have errors
            revised_solutions = []
            for i, (sol, val) in enumerate(zip(solution_paths, validations)):
                if "VALID" not in val.upper():
                    revised = await self.revise(
                        instruction=f"""Fix the identified error:
                        Original Solution: {sol}
                        Error Diagnosis: {val}
                        Problem Analysis: {problem_analysis}
                        
                        Correct the solution while preserving its core approach.
                        Show corrected work and final numerical answer.""",
                        context=sol
                    )
                    revised_solutions.append(revised)
                else:
                    revised_solutions.append(sol)

            # Ensemble select best solution
            final_answer = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Mathematical correctness (priority #1)
                2. Consistency with problem constraints
                3. Clarity of reasoning steps
                4. Unit consistency throughout
                5. Real-world plausibility
                
                Extract only the final numerical answer from the selected solution.
                If multiple are equally valid, choose the one with clearest step-by-step reasoning.
                
                Return ONLY the numerical answer as a string (e.g., "7500" or "40.5").""",
                contexts_list=revised_solutions
            )

        # FINAL VERIFICATION & EXTRACTION
        verified_answer = await self.generate(
            instruction=f"""Final Verification:
            Problem: {self.problem_text}
            Analysis: {problem_analysis}
            Raw Answer: {final_answer}
            
            Ensure the answer:
            1. Is a single numerical value (integer or decimal)
            2. Matches expected format from analysis
            3. Satisfies all real-world constraints
            4. Is extracted cleanly (no units, no text, just number)
            
            If answer is not clean numerical value, extract the number.
            If answer violates constraints, return "ERROR" and explain why.
            
            Return ONLY the final numerical answer or "ERROR".""",
            context=final_answer
        )

        # Clean extraction (remove any remaining text)
        clean_extraction = await self.generate(
            instruction=f"""Extract ONLY the numerical answer from this text:
            {verified_answer}
            
            Remove any units, explanations, or surrounding text.
            Return just the number as string (e.g., "7500", "40.5", "3").
            If no number found, return "0".""",
            context=verified_answer
        )

        return clean_extraction.strip()