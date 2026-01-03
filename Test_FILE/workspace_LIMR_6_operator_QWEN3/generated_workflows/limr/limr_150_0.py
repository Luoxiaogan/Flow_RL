# Workflow ID: limr_150_0
# Benchmark: limr
# Data Indices: [82, 94]

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

        # Step 1: High-level problem classification and strategy generation
        strategy_analysis = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify the problem domain (algebra, geometry, number theory, combinatorics, etc.)
            2. Identify key mathematical objects (functions, equations, geometric figures, sequences)
            3. Determine required proof techniques or computational methods
            4. List potential solution strategies (analytical, computational, combinatorial, etc.)
            5. Flag any special constraints or edge cases
            6. Estimate complexity level (low/medium/high) based on steps required
            Output structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Generate 3 parallel high-level solution approaches
        approach_instructions = [
            """Develop a purely analytical solution approach:
            - Use algebraic manipulation, identities, and mathematical theorems
            - Show step-by-step logical derivation
            - Avoid numerical computation unless absolutely necessary
            - Focus on exact symbolic results""",
            
            """Develop a computational/algorithmic solution approach:
            - Identify what needs to be computed
            - Specify required precision and validation criteria
            - Outline algorithmic steps or code structure
            - Consider edge cases and numerical stability""",
            
            """Develop a hybrid geometric/intuitive approach:
            - Look for visual or geometric interpretations
            - Consider symmetry, invariants, or transformations
            - Use estimation or bounding to verify reasonableness
            - Connect to known mathematical results or theorems"""
        ]

        approaches = await asyncio.gather(
            *[self.generate(instruction=instr, context=strategy_analysis) for instr in approach_instructions]
        )

        # Step 3: Decompose each approach into executable subproblems
        decomposed_approaches = []
        for i, approach in enumerate(approaches):
            try:
                decomposition = await self.decompose(
                    instruction=f"""Decompose Approach {i+1} into atomic subproblems:
                    - Each subproblem should be solvable independently or with specified dependencies
                    - Include prerequisite knowledge or intermediate results needed
                    - Estimate difficulty level for each subproblem
                    - Flag any subproblems that may require computational assistance
                    - Ensure complete coverage of the solution path""",
                    context=approach
                )
                decomposed_approaches.append({
                    'approach': approach,
                    'decomposition': decomposition
                })
            except Exception:
                # Fallback: if decomposition fails, treat entire approach as single subproblem
                decomposed_approaches.append({
                    'approach': approach,
                    'decomposition': [{
                        'id': 'fallback_1',
                        'description': f'Execute entire Approach {i+1} as single step',
                        'dependencies': ''
                    }]
                })

        # Step 4: Solve subproblems in parallel across all approaches
        all_solutions = []
        for approach_data in decomposed_approaches:
            approach = approach_data['approach']
            decomposition = approach_data['decomposition']
            
            # Solve each subproblem in this approach
            subproblem_solutions = {}
            for subproblem in decomposition:
                sub_id = subproblem['id']
                deps = subproblem['dependencies'].split(',') if subproblem['dependencies'] else []
                
                # Wait for dependencies (simplified - in practice would need topological sort)
                dep_context = "\n".join([subproblem_solutions.get(dep, "") for dep in deps if dep in subproblem_solutions])
                
                # Decide whether to use programmer or generate based on subproblem description
                if any(keyword in subproblem['description'].lower() for keyword in ['compute', 'calculate', 'numerical', 'code', 'program']):
                    solution = await self.programmer(
                        instruction=f"""Solve subproblem: {subproblem['description']}
                        Context from dependencies: {dep_context}
                        Approach context: {approach}
                        Strategy analysis: {strategy_analysis}
                        Requirements:
                        - Use exact computation when possible
                        - Validate results against mathematical constraints
                        - Return only the final result with brief explanation""",
                        context=dep_context
                    )
                else:
                    solution = await self.generate(
                        instruction=f"""Solve subproblem: {subproblem['description']}
                        Context from dependencies: {dep_context}
                        Approach context: {approach}
                        Strategy analysis: {strategy_analysis}
                        Requirements:
                        - Show complete mathematical reasoning
                        - Justify each step
                        - Verify intermediate results
                        - Return only the final result with brief explanation""",
                        context=dep_context
                    )
                
                # Revise for clarity and correctness
                revised_solution = await self.revise(
                    instruction="""Improve this solution:
                    - Check for mathematical errors
                    - Ensure logical flow is clear
                    - Verify all assumptions are stated
                    - Confirm final result is consistent with problem constraints
                    - Format as: 'Result: [value]' followed by brief justification""",
                    context=solution
                )
                subproblem_solutions[sub_id] = revised_solution
            
            # Combine subproblem solutions into complete approach solution
            combined_solution = "\n\n".join([
                f"Subproblem {sub_id}: {solution}" 
                for sub_id, solution in subproblem_solutions.items()
            ])
            
            final_approach_solution = await self.generate(
                instruction=f"""Synthesize complete solution from subproblems:
                Original approach: {approach}
                Subproblem solutions: {combined_solution}
                Requirements:
                - Integrate all subproblem results into coherent whole
                - Highlight key insights and critical steps
                - Verify final answer satisfies original problem
                - Format final answer as: 'FINAL ANSWER: [integer]'""",
                context=combined_solution
            )
            
            all_solutions.append(final_approach_solution)

        # Step 5: Ensemble - select best solution or synthesize
        final_answer = await self.ensemble(
            instruction="""Select the best solution or synthesize from multiple:
            Evaluation criteria:
            1. Mathematical correctness and rigor
            2. Completeness of reasoning
            3. Clarity of presentation
            4. Alignment with problem constraints
            5. Final answer is integer between 000-999
            
            If solutions conflict:
            - Prefer analytical over computational when both are rigorous
            - Prefer solutions with complete step-by-step derivation
            - Cross-validate numerical results with analytical bounds
            
            Output format:
            - Start with 'SELECTED SOLUTION: [index]'
            - Then provide the complete selected solution
            - End with 'FINAL ANSWER: [integer]' on its own line""",
            contexts_list=all_solutions
        )

        # Step 6: Final validation and formatting
        validated_answer = await self.revise(
            instruction="""Final validation and formatting:
            1. Extract the final answer (must be integer 000-999)
            2. If multiple answers exist, select the one with strongest derivation
            3. If no clear answer, return 000 with explanation
            4. Format output as exactly: 'FINAL ANSWER: XXX' where XXX is 3-digit integer
            5. Remove all other text - only return the formatted answer""",
            context=final_answer
        )

        # Extract just the final answer in required format
        match = re.search(r'FINAL ANSWER:\s*(\d{1,3})', validated_answer)
        if match:
            answer = match.group(1).zfill(3)  # Ensure 3-digit format
            return f"FINAL ANSWER: {answer}"
        else:
            # Fallback if extraction fails
            return "FINAL ANSWER: 000"