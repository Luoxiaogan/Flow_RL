# Workflow ID: limr_165_0
# Benchmark: limr
# Data Indices: [260, 131]

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

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify the primary mathematical domain (algebra, combinatorics, number theory, geometry, etc.)
            2. Determine the solution type required (exact value, proof, optimization, probability, etc.)
            3. List all explicit and implicit constraints
            4. Identify key variables and their domains
            5. Suggest 3 potential solution approaches with brief rationale for each
            6. Flag any potential edge cases or special conditions
            Format as structured JSON with keys: domain, solution_type, constraints, variables, approaches, edge_cases""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        # Extract suggested approaches for parallel exploration
        approach_analysis = await self.generate(
            instruction=f"""Based on classification:
            {classification}
            
            Generate detailed solution plans for each of the 3 suggested approaches. For each approach:
            - Outline step-by-step methodology
            - Identify required mathematical tools/theorems
            - Estimate computational complexity
            - List potential failure points
            - Suggest verification methods
            Format each approach as a numbered section with clear headings.""",
            context=classification
        )

        # PHASE 3: PROBLEM DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break down the problem into atomic subproblems:
            1. Identify minimal independent subproblems
            2. Establish dependency relationships between subproblems
            3. For each subproblem, specify:
               - Required inputs
               - Expected outputs
               - Mathematical domain
               - Suggested solution method (symbolic, computational, geometric, etc.)
            4. Flag any subproblems that may have multiple valid solutions
            5. Identify subproblems that serve as verification checkpoints for others
            Return structured list of subproblems with dependencies.""",
            context=approach_analysis
        )

        # PHASE 4: PARALLEL SUBPROBLEM SOLVING
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            dependencies = subproblem.get('dependencies', '')
            
            # Determine solution strategy based on subproblem characteristics
            strategy = await self.generate(
                instruction=f"""For subproblem {sub_id}: "{description}"
                Analyze the most appropriate solution method:
                - Should this be solved symbolically, computationally, or geometrically?
                - What specific mathematical tools are required?
                - Are there any special considerations or optimizations?
                Return a concise strategy recommendation.""",
                context=f"Full decomposition: {json.dumps(decomposition)}"
            )
            
            # Execute based on strategy
            if "computational" in strategy.lower() or "program" in strategy.lower() or "calculate" in strategy.lower():
                solution = await self.programmer(
                    instruction=f"""Solve subproblem {sub_id}: {description}
                    Requirements:
                    - Use precise mathematical computation
                    - Show all steps in code comments
                    - Include verification checks
                    - Return final answer in specified format
                    - Handle edge cases appropriately""",
                    context=strategy
                )
            else:
                solution = await self.generate(
                    instruction=f"""Solve subproblem {sub_id}: {description}
                    Requirements:
                    - Show complete mathematical reasoning
                    - Justify each step with appropriate theorems or principles
                    - Include verification of intermediate results
                    - Consider alternative approaches if stuck
                    - Format final answer clearly""",
                    context=strategy
                )
            
            # Verify solution
            verified_solution = await self.revise(
                instruction=f"""Critically verify the solution for subproblem {sub_id}:
                - Check for mathematical errors
                - Verify adherence to constraints
                - Test edge cases
                - Ensure answer format matches requirements
                - If errors found, correct them and explain the correction
                Return the verified solution with verification notes.""",
                context=solution
            )
            
            return {
                'id': sub_id,
                'description': description,
                'solution': verified_solution,
                'strategy': strategy
            }

        # Solve all subproblems in parallel
        subproblem_tasks = [solve_subproblem(sp) for sp in decomposition]
        subproblem_solutions = await asyncio.gather(*subproblem_tasks)
        
        # Create solution map for dependency resolution
        solution_map = {sol['id']: sol for sol in subproblem_solutions}

        # PHASE 5: SOLUTION SYNTHESIS
        synthesis_context = "\n\n".join([
            f"Subproblem {sol['id']}: {sol['description']}\nSolution: {sol['solution']}\nStrategy: {sol['strategy']}"
            for sol in subproblem_solutions
        ])

        synthesized_solution = await self.generate(
            instruction=f"""Synthesize complete solution from subproblem solutions:
            {synthesis_context}
            
            Requirements:
            - Integrate all subproblem solutions into coherent final answer
            - Ensure logical flow between subproblems
            - Verify that dependencies are properly respected
            - Cross-validate results where possible
            - Format final answer as required (typically integer 000-999)
            - Include brief justification for final answer""",
            context=synthesis_context
        )

        # PHASE 6: MULTI-ANGLE VERIFICATION
        verification_tasks = [
            self.generate(
                instruction=f"""Verify solution from mathematical rigor perspective:
                - Check logical consistency
                - Verify theorem applications
                - Ensure no steps are skipped
                - Confirm answer format requirements are met""",
                context=synthesized_solution
            ),
            self.generate(
                instruction=f"""Verify solution from edge case perspective:
                - Test boundary conditions
                - Check special cases mentioned in problem
                - Verify handling of constraints
                - Consider alternative interpretations""",
                context=synthesized_solution
            ),
            self.programmer(
                instruction=f"""Verify solution computationally where possible:
                - Implement key calculations
                - Test with sample values
                - Verify numerical results
                - Check for off-by-one errors or precision issues""",
                context=synthesized_solution
            )
        ]

        verification_results = await asyncio.gather(*verification_tasks)

        # PHASE 7: FINAL ENSEMBLE & REFINEMENT
        final_answer = await self.ensemble(
            instruction="""Synthesize the best final answer from all available solutions and verifications:
            - Prioritize solutions with multiple verification methods confirming results
            - Resolve any conflicts between approaches
            - Ensure answer is in required format (integer 000-999)
            - Include concise justification
            - If uncertainty remains, indicate confidence level and rationale
            Return ONLY the final answer as a three-digit integer (000-999) with no additional text.""",
            contexts_list=[synthesized_solution] + verification_results
        )

        # PHASE 8: FINAL VALIDATION & FORMATTING
        formatted_answer = await self.revise(
            instruction="""Ensure final answer meets all requirements:
            - Must be exactly three digits (000-999)
            - No decimal points or fractions
            - No explanatory text
            - If answer is less than 100, pad with leading zeros
            - If multiple valid answers, select the one best supported by evidence
            Return ONLY the three-digit integer.""",
            context=final_answer
        )

        # Extract just the three-digit number
        import re
        match = re.search(r'\b\d{3}\b', formatted_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return first three digits found
            digits = re.findall(r'\d', formatted_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            else:
                # Last resort: return 000 (should never happen with proper workflow)
                return "000"