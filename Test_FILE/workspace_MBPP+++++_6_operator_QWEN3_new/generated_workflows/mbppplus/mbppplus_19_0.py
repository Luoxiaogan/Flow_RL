# Workflow ID: mbppplus_19_0
# Benchmark: mbppplus
# Data Indices: [105, 322]

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

        # Step 1: Classify the problem type and complexity
        classification = await self.generate(
            instruction="""Thoroughly analyze the problem and classify it by:
            1. Primary category: Is it about sets/lists, strings, math, recursion, or logic?
            2. Algorithmic pattern: Does it require brute force, dynamic programming, greedy, divide-and-conquer, or simple iteration?
            3. Edge case sensitivity: What edge cases are critical? (empty inputs, singles, duplicates, negatives, etc.)
            4. Return type constraints: Must it return list, tuple, set, int, bool, etc.?
            5. Complexity level: Simple (direct), Medium (needs 1-2 steps), Complex (needs decomposition).
            Format your response as a structured JSON-like summary with these keys.""",
            context=""
        )

        # Step 2: Strategy selection based on classification
        strategy = "direct"
        if "dynamic programming" in classification.lower() or "recursion" in classification.lower() or "complex" in classification.lower():
            strategy = "decompose"
        elif "multiple approaches" in classification.lower() or "ambiguous" in classification.lower():
            strategy = "ensemble"

        # Step 3: Execute selected strategy
        if strategy == "decompose":
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal, independent, solvable subproblems.
                Each subproblem should:
                - Be clearly defined with inputs and expected outputs
                - Have no circular dependencies
                - Be solvable in isolation or with specified dependencies
                - Contribute directly to the final solution
                Return as list of subproblem dicts with 'id', 'description', 'dependencies'.""",
                context=classification
            )
            
            # Solve subproblems in parallel where possible
            solutions = {}
            for sp in subproblems:
                # Check dependencies
                deps_met = True
                if sp.get('dependencies'):
                    for dep_id in sp['dependencies'].split(','):
                        dep_id = dep_id.strip()
                        if dep_id and dep_id not in solutions:
                            deps_met = False
                            break
                if not deps_met:
                    continue  # Will be handled in later iteration or fail gracefully
                
                # Generate solution for this subproblem
                sol = await self.programmer(
                    instruction=f"""Solve this subproblem in isolation:
                    {sp['description']}
                    
                    Context from problem classification:
                    {classification}
                    
                    Ensure:
                    - Handle edge cases specific to this subproblem
                    - Return correct data type
                    - Code is efficient and clean""",
                    context="",
                    max_retries=2
                )
                solutions[sp['id']] = sol
            
            # Synthesize final solution from subproblem solutions
            synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k,v in solutions.items()])
            final_attempt = await self.generate(
                instruction=f"""Synthesize a complete solution using these subproblem solutions:
                {synthesis_context}
                
                Reconstruct the full answer following the original problem's requirements.
                Ensure type consistency and edge case handling as per classification:
                {classification}""",
                context=synthesis_context
            )
            
        elif strategy == "ensemble":
            # Generate multiple solution attempts in parallel
            attempts = await asyncio.gather(
                self.programmer(
                    instruction=f"""Solve using a mathematical/algorithmic approach. Be precise and efficient.
                    Classification context: {classification}""",
                    context="",
                    max_retries=2
                ),
                self.programmer(
                    instruction=f"""Solve using a brute-force or iterative approach. Prioritize correctness over efficiency.
                    Classification context: {classification}""",
                    context="",
                    max_retries=2
                ),
                self.generate(
                    instruction=f"""Reason step by step without code. Derive the answer through logical deduction.
                    Classification context: {classification}""",
                    context=""
                )
            )
            
            # Ensemble select best or synthesize
            final_attempt = await self.ensemble(
                instruction="""Select the most correct, efficient, and robust solution.
                Criteria:
                1. Correctness on edge cases (empty, single, duplicates, boundaries)
                2. Type consistency with problem requirements
                3. Algorithmic efficiency
                4. Code clarity and maintainability
                If multiple are strong, synthesize a hybrid solution.""",
                contexts_list=attempts
            )
            
        else:  # direct strategy
            final_attempt = await self.programmer(
                instruction=f"""Generate a direct, optimal solution.
                Classification context: {classification}
                Requirements:
                - Handle all edge cases mentioned in classification
                - Return correct data type
                - Be efficient and clean
                - Include comments if complex logic""",
                context="",
                max_retries=3
            )

        # Step 4: Validation and edge case injection
        validated = await self.revise(
            instruction=f"""Critically review this solution:
            {final_attempt}
            
            Based on problem classification:
            {classification}
            
            Inject and handle these edge cases explicitly:
            - Empty inputs
            - Single element inputs
            - Duplicate elements
            - Boundary values (0, negative, max/min)
            - Type mismatches or conversions
            - Order preservation if required
            
            Return a revised, robust version that explicitly addresses these.
            If fundamental flaws found, completely rewrite with correct approach.""",
            context=final_attempt
        )

        # Step 5: Final type and format enforcement
        final_output = await self.revise(
            instruction=f"""Ensure final output matches EXACT requirements from original problem.
            - Function name must match exactly
            - Parameter names must match
            - Return type must be correct (list vs tuple vs set vs int vs bool)
            - No extra prints or outputs
            - Only the function implementation with necessary imports at top
            
            If any deviation, correct it now.
            
            Classification for reference:
            {classification}""",
            context=validated
        )

        return final_output