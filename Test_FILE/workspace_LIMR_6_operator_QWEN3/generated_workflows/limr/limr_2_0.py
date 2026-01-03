# Workflow ID: limr_2_0
# Benchmark: limr
# Data Indices: [340, 295]

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

        # STEP 1: Deep Problem Classification
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this mathematical problem. Analyze:
            1. Primary domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Solution archetypes likely required (substitution, transformation, induction, symmetry, modular arithmetic, coordinate geometry, recursive decomposition, etc.)
            3. Key mathematical objects involved (functions, sequences, polynomials, geometric figures, etc.)
            4. Constraints and boundary conditions
            5. Expected answer format and type
            6. Potential pitfalls or deceptive elements
            7. Recommended solution strategy (1-2 sentences)
            Output in structured markdown format with clear section headers.""",
            context=""
        )

        # STEP 2: Parallel Hypothesis Generation
        # Generate 3 different solution approaches based on classification
        approach_instructions = [
            """Develop a solution assuming this is primarily an ALGEBRAIC TRANSFORMATION problem. Focus on:
            - Variable substitution and equation manipulation
            - Logarithmic/exponential identities if applicable
            - Functional equation techniques
            - Domain/range considerations
            Show all steps clearly and justify each transformation.""",
            
            """Develop a solution assuming this is primarily a NUMBER THEORETIC / MODULAR problem. Focus on:
            - Prime factorization and divisibility
            - Modular arithmetic and congruences
            - Diophantine equation techniques
            - Properties of integers and their relationships
            Show all steps clearly and justify each number theoretic step.""",
            
            """Develop a solution assuming this is primarily a COMBINATORIAL / STRUCTURAL problem. Focus on:
            - Counting principles and combinatorial identities
            - Case analysis and partitioning
            - Graph theory or set theory approaches if applicable
            - Optimization through combinatorial reasoning
            Show all steps clearly and justify each combinatorial argument."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in approach_instructions]
        )

        # STEP 3: Conditional Decomposition (if problem appears multi-step)
        decomposition_needed = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Determine if this problem requires hierarchical decomposition into subproblems. 
            Answer only 'YES' or 'NO'.""",
            context=classification
        )

        if "YES" in decomposition_needed.upper():
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal independent subproblems. For each:
                - Clearly state what needs to be solved
                - Specify any dependencies on other subproblems
                - Indicate if it's computational (suitable for Programmer) or analytical
                Prioritize subproblems that can be solved in parallel.""",
                context=classification
            )
            
            # Solve subproblems in topological order (simplified: solve all with asyncio.gather)
            subproblem_solutions = []
            for subproblem in subproblems:
                if "computational" in subproblem['description'].lower() or "calculate" in subproblem['description'].lower():
                    solution = await self.programmer(
                        instruction=f"Solve this subproblem: {subproblem['description']}",
                        context=classification
                    )
                else:
                    solution = await self.generate(
                        instruction=f"""Solve this subproblem analytically: {subproblem['description']}
                        Show all reasoning steps clearly.""",
                        context=classification
                    )
                subproblem_solutions.append(solution)
            
            # Integrate subproblem solutions
            integrated_solution = await self.generate(
                instruction=f"""Integrate these subproblem solutions into a complete answer:
                {chr(10).join(subproblem_solutions)}
                
                Ensure logical flow and consistency between subproblems.
                Derive the final answer from the integrated solution.""",
                context=classification
            )
            hypotheses.append(integrated_solution)

        # STEP 4: Adversarial Validation Loop
        current_best = await self.ensemble(
            instruction="""Select the most promising solution from the candidates. Criteria:
            - Mathematical rigor and completeness
            - Clarity of reasoning
            - Alignment with problem constraints
            - Efficiency of approach
            If multiple are strong, synthesize the best elements into one coherent solution.""",
            contexts_list=hypotheses
        )

        for iteration in range(3):  # Max 3 refinement loops
            validation = await self.generate(
                instruction=f"""Adversarially critique this solution. Assume it contains at least one error. Specifically check:
                - Algebraic manipulations for sign/distribution errors
                - Domain restrictions and edge cases
                - Logical gaps in reasoning
                - Arithmetic miscalculations
                - Answer format compliance (must be integer 000-999)
                If no errors found, state "VALIDATED". Otherwise, list all errors found.""",
                context=current_best
            )

            if "VALIDATED" in validation.upper():
                break
            else:
                current_best = await self.revise(
                    instruction=f"""Fix all errors identified in the validation:
                    {validation}
                    
                    Preserve correct parts of the solution while correcting flaws.
                    Add additional verification steps if needed.
                    Ensure final answer is an integer between 0 and 999.""",
                    context=current_best
                )

        # STEP 5: Final Answer Extraction and Formatting
        final_answer = await self.revise(
            instruction="""Extract the final numerical answer from the solution. 
            - Must be an integer between 0 and 999
            - Format as exactly three digits with leading zeros if necessary (e.g., 007, 420, 999)
            - If answer is not in this range, explain why and suggest corrections
            - Output ONLY the three-digit number, nothing else""",
            context=current_best
        )

        # Clean and return final answer
        # Extract exactly 3 digits from the response
        match = re.search(r'\b(\d{3})\b', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: try to extract any number and format it
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                return "000"  # Ultimate fallback