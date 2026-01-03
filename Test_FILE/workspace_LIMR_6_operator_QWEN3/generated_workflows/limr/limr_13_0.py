# Workflow ID: limr_13_0
# Benchmark: limr
# Data Indices: [124, 28]

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

        # PHASE 1: MULTI-LENS PROBLEM INTERPRETATION
        # Generate parallel interpretations through different mathematical lenses
        interpretation_instructions = [
            """Analyze this problem through an ALGEBRAIC lens:
            - Identify all variables, equations, and functional relationships
            - Determine if polynomial, rational, exponential, or logarithmic structures exist
            - Note any symmetries, substitutions, or transformations that could simplify
            - Suggest algebraic techniques (factoring, completing square, etc.)""",
            
            """Analyze this problem through a NUMBER THEORY lens:
            - Identify all numerical constants and their potential significance
            - Check for modular arithmetic, divisibility, or base representation clues
            - Note prime factors, perfect powers, or special number properties
            - Suggest number theory techniques (CRT, Fermat, Euler, etc.)""",
            
            """Analyze this problem through a COMBINATORIAL/LOGICAL lens:
            - Identify counting elements, probability spaces, or logical constraints
            - Note any permutations, combinations, or recursive structures
            - Suggest combinatorial techniques (inclusion-exclusion, generating functions, etc.)
            - Consider edge cases and boundary conditions""",
            
            """Analyze this problem through a COMPUTATIONAL/ALGORITHMIC lens:
            - Identify if brute force, search, or iterative methods could apply
            - Estimate computational complexity and feasible search spaces
            - Note any patterns that could be exploited algorithmically
            - Suggest programming approaches (loops, recursion, memoization)"""
        ]

        interpretations = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in interpretation_instructions]
        )

        # Synthesize interpretations into unified problem understanding
        problem_understanding = await self.ensemble(
            instruction="""Synthesize these mathematical interpretations into a unified problem analysis:
            - Identify the 2-3 most promising solution approaches based on consensus and specificity
            - Note any conflicting interpretations and resolve them by prioritizing approaches with concrete constraints
            - Extract all explicit and implicit constraints (domain restrictions, integer requirements, etc.)
            - Formulate a preliminary solution strategy that combines the strongest elements from each lens
            - Output as a structured analysis with clear sections: Key Constraints, Promising Approaches, Potential Pitfalls""",
            contexts_list=interpretations
        )

        # PHASE 2: DEPENDENCY-AWARE DECOMPOSITION
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal subproblems with explicit dependencies:
            Based on this analysis: {problem_understanding}
            
            Requirements:
            - Each subproblem must be solvable independently given its dependencies
            - Identify which subproblems can be solved in parallel vs. must be sequential
            - For each subproblem, specify required mathematical tools (algebra, number theory, etc.)
            - Include validation criteria for each subproblem's solution
            - Maximum 7 subproblems; if more needed, group related ones
            - Format each as: [ID] Description (Dependencies: [...])""",
            context=problem_understanding
        )

        # PHASE 3: PARALLEL SUBPROBLEM SOLVING WITH VALIDATION
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            dependencies = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            
            # Build context from dependencies if they exist
            dependency_context = ""
            if dependencies and dependencies[0]:  # if not empty
                dependency_context = f"Based on solutions to: {', '.join(dependencies)}"
            
            # Generate initial solution attempt
            solution_attempt = await self.generate(
                instruction=f"""Solve this subproblem: {sp_desc}
                {dependency_context}
                
                Requirements:
                - Show all mathematical steps clearly
                - Justify each transformation or assumption
                - If stuck, suggest alternative approaches from other mathematical lenses
                - End with a clear statement of the subproblem's solution""",
                context=dependency_context
            )
            
            # Validate solution
            validation = await self.generate(
                instruction=f"""Critically validate this solution: {solution_attempt}
                
                Validation checklist:
                1. Does it satisfy all constraints from the original problem?
                2. Are all mathematical operations valid (no division by zero, etc.)?
                3. Is the solution consistent with dependency solutions (if any)?
                4. Does it avoid circular reasoning or unwarranted assumptions?
                5. Is the final answer format appropriate for this subproblem?
                
                If any issues found, explain them clearly. If valid, state "VALID: [summary]".""",
                context=solution_attempt
            )
            
            # If validation fails, attempt revision with programmer assistance
            if "VALID:" not in validation:
                # Try computational approach
                programmer_attempt = await self.programmer(
                    instruction=f"""Implement a computational solution for: {sp_desc}
                    
                    Context: {solution_attempt}
                    Validation issues: {validation}
                    
                    Requirements:
                    - Write Python code to solve or verify the subproblem
                    - Include bounds and constraints from the original problem
                    - Output should be the exact solution value(s)
                    - Handle edge cases explicitly""",
                    context=solution_attempt,
                    max_retries=2
                )
                
                # Revise original solution with computational insights
                revised_solution = await self.revise(
                    instruction=f"""Incorporate insights from computational verification: {programmer_attempt}
                    
                    Revise the original solution to address validation issues: {validation}
                    Maintain mathematical rigor while integrating computational results.
                    If computational approach is superior, adopt it as primary solution.""",
                    context=solution_attempt
                )
                return revised_solution
            else:
                return solution_attempt

        # Solve subproblems respecting dependencies
        subproblem_solutions = {}
        remaining_subproblems = {sp['id']: sp for sp in decomposition}
        
        # Simple dependency resolution (could be enhanced with topological sort for complex cases)
        max_iterations = len(decomposition) * 2
        iteration = 0
        
        while remaining_subproblems and iteration < max_iterations:
            solvable = []
            for sp_id, subproblem in remaining_subproblems.items():
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                if all(dep.strip() in subproblem_solutions for dep in deps if dep.strip()):
                    solvable.append((sp_id, subproblem))
            
            if not solvable:
                break  # Deadlock - proceed with what we have
            
            # Solve solvable subproblems in parallel
            solutions = await asyncio.gather(
                *[solve_subproblem(sp) for _, sp in solvable]
            )
            
            # Store solutions
            for (sp_id, _), solution in zip(solvable, solutions):
                subproblem_solutions[sp_id] = solution
                del remaining_subproblems[sp_id]
            
            iteration += 1

        # PHASE 4: SYNTHESIZE AND VERIFY GLOBAL SOLUTION
        all_solutions_text = "\n\n".join([f"Subproblem {sp_id}: {solution}" for sp_id, solution in subproblem_solutions.items()])
        
        global_synthesis = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into a complete answer:
            Subproblem solutions: {all_solutions_text}
            
            Requirements:
            - Combine results logically to answer the original question
            - Verify that final answer satisfies ALL original constraints
            - Check for consistency across subproblems
            - If multiple answer candidates exist, resolve using problem constraints
            - Final answer must be an integer between 000 and 999
            - Present final answer in format: "FINAL ANSWER: XXX" where XXX is the 3-digit integer""",
            context=all_solutions_text
        )

        # Final validation and extraction
        final_answer = await self.revise(
            instruction="""Extract and verify the final answer:
            - Scan the entire solution for any integer between 000 and 999
            - Verify this answer satisfies ALL problem constraints
            - If multiple candidates, select the one most consistent with complete solution
            - If no valid candidate, state "NO VALID ANSWER FOUND"
            - Output ONLY the 3-digit integer (000-999) or "NO VALID ANSWER FOUND"
            - Do not include any other text or explanation""",
            context=global_synthesis
        )

        # Fallback: if no answer found, attempt direct computational solution
        if "NO VALID ANSWER" in final_answer:
            direct_computational = await self.programmer(
                instruction="""Solve the original problem computationally:
                - Implement brute force or algorithmic solution
                - Search space: integers 0-999
                - Verify each candidate against original problem constraints
                - Return the first valid answer found
                - If none found in range, return 000""",
                context="",
                max_retries=3
            )
            
            # Extract just the number from computational result
            final_answer = await self.generate(
                instruction="""Extract only the 3-digit answer from this computational result:
                - If result contains multiple numbers, select the one between 000-999
                - If no number in range, return 000
                - Output ONLY the 3-digit integer with no other text""",
                context=direct_computational
            )

        return final_answer.strip()