# Workflow ID: mbppplus_179_0
# Benchmark: mbppplus
# Data Indices: [369, 108]

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
        import re

        # Step 1: Classify the problem and extract key requirements
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it:
            1. What is the primary task? (e.g., comparison, transformation, aggregation, calculation)
            2. What are the input types and structures? (e.g., list of tuples, integers, strings)
            3. What is the exact expected output type and format? (e.g., integer, stringified dict, list)
            4. What are potential edge cases? (e.g., empty inputs, single elements, duplicates, type boundaries)
            5. Are there any implicit constraints or assumptions?
            6. What category does this fall under? (Simple Operation, Data Transformation, Mathematical, String Processing, Logic)
            Provide a structured, detailed classification to guide subsequent steps.""",
            context=""
        )

        # Step 2: Determine complexity and decide whether to decompose
        complexity_analysis = await self.generate(
            instruction=f"""Based on this classification:
            {classification}
            
            Assess the problem's complexity:
            - Is it a simple, single-step operation? (e.g., min_of_two)
            - Does it require multi-step processing? (e.g., get_unique with grouping and counting)
            - Are there interdependent subproblems?
            - Would decomposition improve solution quality?
            
            Respond with either 'SIMPLE' or 'COMPLEX' followed by a brief justification.""",
            context=classification
        )

        # Step 3: Conditional branching based on complexity
        if "SIMPLE" in complexity_analysis.upper():
            # Direct code generation for simple problems
            solution_attempt = await self.programmer(
                instruction=f"""Generate a Python function that solves the problem.
                Classification context: {classification}
                
                Requirements:
                - Use the exact function signature specified in the problem.
                - Handle all identified edge cases.
                - Return the correct data type and format.
                - Prioritize clarity and correctness over premature optimization.
                - Include necessary imports within the function if needed.
                
                Generate only the function implementation as specified in the output requirements.""",
                context=classification,
                max_retries=3
            )
            
            # Validate and refine in a loop
            for attempt in range(3):
                validation = await self.generate(
                    instruction=f"""Critically validate this solution:
                    {solution_attempt}
                    
                    Check for:
                    1. Correct function signature
                    2. Proper handling of edge cases
                    3. Exact return type and format compliance
                    4. Logical correctness
                    5. Potential bugs or oversights
                    
                    If any issues are found, describe them specifically. If perfect, respond with 'VALID'.""",
                    context=solution_attempt
                )
                
                if "VALID" in validation.upper():
                    return solution_attempt
                
                # Revise based on validation feedback
                solution_attempt = await self.revise(
                    instruction=f"""Fix all issues identified in the validation:
                    {validation}
                    
                    Improve the solution while maintaining the exact function signature and return format.
                    Ensure edge cases are handled and logic is sound.""",
                    context=solution_attempt
                )
            
            return solution_attempt  # Return best attempt after retries

        else:
            # Complex problem: decompose into subproblems
            decomposition = await self.decompose(
                instruction=f"""Break down this complex problem into manageable subproblems:
                Classification: {classification}
                
                For each subproblem:
                - Clearly define what needs to be solved
                - Specify any dependencies on other subproblems
                - Identify required inputs and expected outputs
                - Note any edge cases specific to this subproblem
                
                Ensure the decomposition is complete and logically ordered.""",
                context=classification
            )

            # Generate solutions for each subproblem in parallel
            subproblem_solutions = []
            for subproblem in decomposition:
                sub_solution = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context from problem classification:
                    {classification}
                    
                    Requirements:
                    - Focus only on this subproblem
                    - Handle its specific edge cases
                    - Return appropriate intermediate result
                    - Keep code modular and testable""",
                    context=subproblem['description'],
                    max_retries=2
                )
                subproblem_solutions.append(sub_solution)

            # Synthesize subproblem solutions into final solution
            synthesis_context = "\n\n".join([
                f"Subproblem {i+1}: {decomposition[i]['description']}\nSolution: {subproblem_solutions[i]}"
                for i in range(len(decomposition))
            ])

            synthesized_solution = await self.generate(
                instruction=f"""Synthesize these subproblem solutions into a complete, cohesive function:
                {synthesis_context}
                
                Classification context: {classification}
                
                Requirements:
                - Integrate all subproblem solutions logically
                - Maintain correct function signature
                - Ensure proper data flow between subproblems
                - Handle all edge cases identified in classification
                - Return output in exact required format
                - Optimize for readability and maintainability
                
                Generate only the final function implementation as specified.""",
                context=synthesis_context
            )

            # Generate multiple solution candidates in parallel for ensemble selection
            candidate_solutions = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate Solution Candidate 1:
                    Focus on correctness and edge case handling.
                    Classification: {classification}
                    Decomposition: {synthesis_context}""",
                    context=synthesis_context,
                    max_retries=2
                ),
                self.programmer(
                    instruction=f"""Generate Solution Candidate 2:
                    Focus on efficiency and clean code structure.
                    Classification: {classification}
                    Decomposition: {synthesis_context}""",
                    context=synthesis_context,
                    max_retries=2
                ),
                self.programmer(
                    instruction=f"""Generate Solution Candidate 3:
                    Focus on readability and explicit handling of edge cases.
                    Classification: {classification}
                    Decomposition: {synthesis_context}""",
                    context=synthesis_context,
                    max_retries=2
                )
            )

            # Ensemble: select or merge the best solution
            final_solution = await self.ensemble(
                instruction="""Select the best solution or synthesize elements from multiple candidates.
                Criteria:
                1. Correctness (most important)
                2. Edge case coverage
                3. Code clarity and maintainability
                4. Adherence to exact output format
                5. Efficiency (secondary to correctness)
                
                If one solution is clearly superior, select it. Otherwise, merge the best elements.
                Return only the final function implementation as specified in output requirements.""",
                contexts_list=candidate_solutions
            )

            # Final validation and refinement loop
            for attempt in range(2):
                final_validation = await self.generate(
                    instruction=f"""Perform final validation on this solution:
                    {final_solution}
                    
                    Check:
                    1. Function signature matches exactly
                    2. Return type and format are correct
                    3. All edge cases from classification are handled
                    4. No logical errors or oversights
                    5. Code is clean and follows best practices
                    
                    If perfect, respond 'FINAL_VALID'. Otherwise, describe specific issues.""",
                    context=final_solution
                )
                
                if "FINAL_VALID" in final_validation.upper():
                    return final_solution
                
                final_solution = await self.revise(
                    instruction=f"""Fix all issues identified:
                    {final_validation}
                    
                    Make minimal necessary changes to achieve correctness and compliance.
                    Preserve the function signature and return format exactly.""",
                    context=final_solution
                )
            
            return final_solution