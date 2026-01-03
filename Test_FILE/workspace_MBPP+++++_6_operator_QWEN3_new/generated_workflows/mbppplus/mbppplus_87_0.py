# Workflow ID: mbppplus_87_0
# Benchmark: mbppplus
# Data Indices: [300, 359]

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
        
        # Phase 1: Multi-perspective problem analysis
        analysis_instructions = [
            """Analyze this programming problem from a MATHEMATICAL perspective:
            - Identify any underlying mathematical principles or formulas needed
            - Determine if number theory, combinatorics, or algebraic manipulation is involved
            - Note any mathematical optimizations possible (like reducing search space)
            - Identify numerical edge cases (zero, one, negatives, large numbers)""",
            
            """Analyze this programming problem from an ALGORITHMIC perspective:
            - Determine if recursion, iteration, or direct computation is most appropriate
            - Identify data structures needed (arrays, sets, dictionaries, etc.)
            - Note algorithmic complexity considerations
            - Identify logical edge cases (empty inputs, single elements, duplicates)""",
            
            """Analyze this programming problem from an IMPLEMENTATION perspective:
            - Identify exact function signature requirements
            - Note required return types and parameter types
            - Identify any implicit constraints from test cases
            - List common implementation pitfalls for this problem type"""
        ]
        
        analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in analysis_instructions]
        )
        
        # Synthesize analyses into unified strategy
        unified_strategy = await self.ensemble(
            instruction="""Synthesize these three analyses into a comprehensive solution strategy:
            - Combine mathematical insights with algorithmic approaches
            - Prioritize implementation requirements and constraints
            - Create a step-by-step plan that addresses all identified edge cases
            - Specify the exact approach (recursive, iterative, mathematical formula, etc.)
            - Include specific instructions for handling boundary conditions
            Output should be a detailed, actionable plan for implementation.""",
            contexts_list=analyses
        )
        
        # Phase 2: Problem decomposition
        decomposition = await self.decompose(
            instruction="""Break down the solution strategy into independent subproblems:
            Each subproblem should be:
            - Self-contained and clearly defined
            - Have minimal dependencies on other subproblems
            - Focus on a specific aspect (edge case handling, core logic, optimization, etc.)
            - Include explicit instructions for implementation
            Return as structured subproblems with dependencies.""",
            context=unified_strategy
        )
        
        # Phase 3: Parallel solution generation and critique
        async def solve_and_critique(subproblem):
            # Generate solution for subproblem
            solution_attempt = await self.programmer(
                instruction=f"""Implement this subproblem:
                {subproblem['description']}
                
                Requirements:
                - Handle all edge cases explicitly
                - Match exact function signature from original problem
                - Return correct data type
                - Include necessary imports
                - Write clean, efficient code
                - Add comments explaining key logic steps""",
                context=unified_strategy,
                max_retries=3
            )
            
            # Critique the solution
            critique = await self.revise(
                instruction="""Critically review this code:
                - Check for edge case handling (empty inputs, boundaries, etc.)
                - Verify type consistency and return type
                - Look for off-by-one errors or logical flaws
                - Assess efficiency and potential optimizations
                - Ensure code matches problem requirements exactly
                - Flag any unsafe or incorrect operations
                Provide detailed feedback with specific line references if possible.""",
                context=solution_attempt
            )
            
            return {
                'subproblem_id': subproblem['id'],
                'solution': solution_attempt,
                'critique': critique,
                'needs_revision': any(x in critique.lower() for x in ['error', 'bug', 'flaw', 'incorrect', 'missing', 'not handle'])
            }
        
        # Execute all subproblems in parallel
        subproblem_results = await asyncio.gather(
            *[solve_and_critique(sp) for sp in decomposition]
        )
        
        # Phase 4: Iterative refinement loop
        max_iterations = 3
        current_solutions = {res['subproblem_id']: res for res in subproblem_results}
        
        for iteration in range(max_iterations):
            # Check if any solutions need revision
            needs_revision = [res for res in current_solutions.values() if res['needs_revision']]
            if not needs_revision:
                break
                
            # Generate targeted revisions
            revision_tasks = []
            for res in needs_revision:
                # Summarize the critique to extract core issues
                issue_summary = await self.summarize(
                    instruction="""Extract the core issues from this critique:
                    - List specific problems found (be concrete)
                    - Prioritize by severity
                    - Suggest specific fixes for each issue
                    - Keep it concise but comprehensive""",
                    context=res['critique']
                )
                
                # Generate revised solution
                revised_solution = await self.programmer(
                    instruction=f"""Revise this solution based on the critique:
                    Original solution:
                    {res['solution']}
                    
                    Critique summary:
                    {issue_summary}
                    
                    Requirements:
                    - Fix all identified issues
                    - Maintain all previous functionality
                    - Keep code clean and well-commented
                    - Ensure edge cases are properly handled
                    - Match exact function signature from original problem""",
                    context=f"{unified_strategy}\n\nPrevious solution:\n{res['solution']}\n\nCritique:\n{issue_summary}",
                    max_retries=2
                )
                
                # Critique the revised solution
                revised_critique = await self.revise(
                    instruction="""Critically review this revised code:
                    - Verify that all previous issues have been addressed
                    - Check for any new issues introduced
                    - Ensure edge cases are now properly handled
                    - Confirm type consistency and return type
                    - Assess overall correctness and efficiency""",
                    context=revised_solution
                )
                
                revision_tasks.append({
                    'subproblem_id': res['subproblem_id'],
                    'solution': revised_solution,
                    'critique': revised_critique,
                    'needs_revision': any(x in revised_critique.lower() for x in ['error', 'bug', 'flaw', 'incorrect', 'missing', 'not handle'])
                })
            
            # Update solutions with revised versions
            revised_results = await asyncio.gather(*[
                asyncio.create_task(asyncio.sleep(0, result=task)) for task in revision_tasks
            ])
            
            for res in revised_results:
                current_solutions[res['subproblem_id']] = res
        
        # Phase 5: Solution synthesis
        all_solutions = [res['solution'] for res in current_solutions.values()]
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize these solution components into a final, complete implementation:
            - Combine the best parts from each solution component
            - Ensure seamless integration between components
            - Verify that all edge cases are handled
            - Confirm correct function signature and return type
            - Optimize for clarity and efficiency
            - Remove any redundant or conflicting code
            - Ensure imports are included at the top
            - Output ONLY the final function implementation with no additional text or explanations""",
            contexts_list=all_solutions
        )
        
        # Phase 6: Final cleanup and validation
        final_implementation = await self.revise(
            instruction="""Perform final cleanup and validation:
            - Ensure output contains ONLY the function implementation
            - Remove any markdown, explanations, or additional text
            - Verify function signature matches exactly what's required
            - Confirm all necessary imports are included
            - Check that code is properly formatted and indented
            - Ensure no print statements or debug code remains
            - Output should be ready for direct execution with no modifications""",
            context=synthesized_solution
        )
        
        # Extract just the code block if it's wrapped in markdown
        code_pattern = r'