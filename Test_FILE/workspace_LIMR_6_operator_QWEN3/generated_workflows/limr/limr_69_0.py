# Workflow ID: limr_69_0
# Benchmark: limr
# Data Indices: [79, 334]

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
        
        # PHASE 1: Deep Structural Analysis
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive mathematical autopsy of this problem:
            1. Classify the problem domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Identify all mathematical objects involved (functions, sequences, polynomials, geometric figures, etc.)
            3. Extract explicit constraints and implicit assumptions
            4. Determine the type of answer required (integer, proof, construction, etc.)
            5. Identify potential solution strategies (algebraic manipulation, calculus, modular arithmetic, combinatorial counting, etc.)
            6. Flag any potential pitfalls or subtle points that could lead to errors
            7. Estimate the complexity level (number of steps, sophistication of techniques required)
            Present your analysis in a structured format with clear section headings.""",
            context=""
        )
        
        # PHASE 2: Hierarchical Decomposition
        subproblems = await self.decompose(
            instruction="""Break this problem down into minimal solvable subproblems:
            - Each subproblem should be independently addressable with a specific mathematical technique
            - Include all dependencies between subproblems
            - Ensure the decomposition covers all aspects needed for a complete solution
            - Prioritize subproblems that can be solved computationally or with known algorithms
            - Include at least one verification subproblem for critical steps
            Format each subproblem with a clear, actionable description.""",
            context=problem_analysis
        )
        
        # Organize subproblems by dependency
        subproblem_dict = {sp['id']: sp for sp in subproblems}
        solved_subproblems = {}
        
        # PHASE 3: Parallel Solution Exploration
        async def solve_subproblem(subproblem_id):
            sp = subproblem_dict[subproblem_id]
            
            # Wait for dependencies
            if sp['dependencies']:
                dep_ids = [d.strip() for d in sp['dependencies'].split(',') if d.strip()]
                for dep_id in dep_ids:
                    if dep_id not in solved_subproblems:
                        await solve_subproblem(dep_id)
            
            # Generate multiple solution approaches in parallel
            approaches = [
                self.generate(
                    instruction=f"""Solve this subproblem using algebraic/analytical methods:
                    Subproblem: {sp['description']}
                    Context from problem analysis: {problem_analysis[:1000]}
                    Previous solutions: {str(solved_subproblems)[:500]}
                    Show all steps clearly and justify each mathematical operation.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve this subproblem using theoretical/conceptual methods:
                    Subproblem: {sp['description']}
                    Consider theorems, properties, and mathematical principles that could apply.
                    Provide rigorous reasoning and cite relevant mathematical concepts.""",
                    context=""
                )
            ]
            
            # Add computational approach if appropriate
            if any(keyword in sp['description'].lower() for keyword in ['compute', 'calculate', 'find value', 'numerical']):
                approaches.append(
                    self.programmer(
                        instruction=f"""Write Python code to solve this subproblem:
                        {sp['description']}
                        Use appropriate libraries (sympy, math, etc.) and ensure precision.
                        Return the exact answer, not an approximation.
                        Include verification steps in your code.""",
                        context=problem_analysis
                    )
                )
            
            # Execute all approaches in parallel
            results = await asyncio.gather(*approaches)
            
            # Validate and synthesize results
            validation = await self.generate(
                instruction=f"""Critically evaluate these solution attempts for subproblem {subproblem_id}:
                {sp['description']}
                
                Evaluate each for:
                - Mathematical correctness
                - Logical consistency
                - Completeness
                - Potential errors or oversights
                Highlight any discrepancies between approaches.
                Recommend the most reliable solution or suggest improvements.""",
                context="\n\n".join(results)
            )
            
            # Ensemble the best solution
            final_solution = await self.ensemble(
                instruction=f"""Synthesize the best solution for subproblem {subproblem_id}:
                {sp['description']}
                
                Consider:
                - Mathematical rigor
                - Computational verification (if available)
                - Elegance and efficiency
                - Consistency with overall problem constraints
                - Verification against edge cases
                Return a single, polished solution with clear reasoning.""",
                contexts_list=results + [validation]
            )
            
            # Store the solution
            solved_subproblems[subproblem_id] = final_solution
            return final_solution
        
        # Solve all subproblems starting from those without dependencies
        root_subproblems = [sp for sp in subproblems if not sp['dependencies']]
        await asyncio.gather(*[solve_subproblem(sp['id']) for sp in root_subproblems])
        
        # PHASE 4: Global Synthesis and Verification
        all_solutions_text = "\n\n".join([f"Subproblem {id}: {solution}" for id, solution in solved_subproblems.items()])
        
        final_answer_draft = await self.generate(
            instruction="""Synthesize all subproblem solutions into a complete answer to the original problem:
            - Ensure logical flow from subproblems to final answer
            - Verify that all constraints are satisfied
            - Cross-check numerical results where possible
            - Present the final answer as an integer between 000 and 999
            - Include brief justification for why this is the correct answer""",
            context=f"Problem Analysis: {problem_analysis}\n\nSubproblem Solutions: {all_solutions_text}"
        )
        
        # PHASE 5: Adversarial Validation and Refinement
        validation = await self.generate(
            instruction="""Play devil's advocate. Try to find flaws in this solution:
            - Are there any mathematical errors?
            - Are there unverified assumptions?
            - Could there be edge cases not considered?
            - Is the final answer format correct (integer 000-999)?
            - Are there alternative interpretations of the problem?
            Be brutally honest and specific.""",
            context=final_answer_draft
        )
        
        refined_answer = await self.revise(
            instruction="""Improve the solution based on the validation feedback:
            - Fix any identified errors
            - Strengthen weak arguments
            - Add missing verification steps
            - Ensure the answer is an integer between 000 and 999
            - Make the reasoning crystal clear and watertight""",
            context=f"Original Solution: {final_answer_draft}\n\nValidation Feedback: {validation}"
        )
        
        # PHASE 6: Final Extraction and Formatting
        final_extraction = await self.generate(
            instruction="""Extract ONLY the final numerical answer from this solution:
            - The answer must be an integer between 000 and 999
            - Remove all reasoning, justifications, and explanations
            - If multiple answers are present, select the one that best fits the problem
            - If no clear answer, return '000' as default
            - Format as exactly three digits (e.g., '042', '123', '999')""",
            context=refined_answer
        )
        
        # Clean and return the final answer
        # Extract first 3-digit number from the response
        match = re.search(r'\b(\d{3})\b', final_extraction)
        if match:
            return match.group(1)
        else:
            # Fallback: try to extract any number and format to 3 digits
            numbers = re.findall(r'\d+', final_extraction)
            if numbers:
                num = int(numbers[0]) % 1000
                return f"{num:03d}"
            else:
                return "000"