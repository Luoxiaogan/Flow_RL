# Workflow ID: limr_71_0
# Benchmark: limr
# Data Indices: [181, 24]

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

        # Step 1: Domain Classification & Strategy Selection
        classification = await self.generate(
            instruction="""Perform deep domain classification and strategy mapping:
            1. Identify primary mathematical domain (algebra, geometry, number theory, combinatorics, optimization).
            2. Detect secondary domains that may be relevant through transformation.
            3. Propose 3 distinct solution strategies with increasing sophistication.
            4. Flag any obvious symmetries, substitutions, or invariants.
            5. Estimate computational vs. symbolic effort ratio.
            Format as structured JSON with keys: primary_domain, secondary_domains, strategies, flags, effort_ratio.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        strategy_contexts = []
        strategies = await self.generate(
            instruction=f"""Extract the three proposed strategies from this classification:
            {classification}
            Return as a numbered list, one strategy per line.""",
            context=classification
        )
        strategy_list = [s.strip() for s in strategies.split('\n') if s.strip()]

        # Limit to 3 strategies for efficiency
        strategy_list = strategy_list[:3]
        
        async def explore_strategy(strategy_desc, idx):
            try:
                # Generate detailed solution path
                solution_draft = await self.generate(
                    instruction=f"""Develop a complete solution path for Strategy {idx + 1}:
                    {strategy_desc}
                    
                    Requirements:
                    - Break into logical steps
                    - Identify key transformations
                    - Specify where symbolic manipulation vs. computation is needed
                    - Note potential failure points
                    - Maintain mathematical rigor throughout""",
                    context=""
                )
                
                # Validate and refine
                validated = await self.revise(
                    instruction="""Critically validate this solution path:
                    - Check for logical gaps or unjustified assumptions
                    - Verify dimensional consistency (if applicable)
                    - Flag any steps requiring computational verification
                    - Suggest improvements for robustness
                    Return in format: VALIDATION: [PASS/FAIL], ISSUES: [comma-separated list], IMPROVEMENTS: [bulleted list]""",
                    context=solution_draft
                )
                
                if "VALIDATION: FAIL" in validated:
                    # Attempt repair
                    repaired = await self.revise(
                        instruction=f"""Repair the solution path using these suggestions:
                        {validated}
                        
                        Requirements:
                        - Address all listed issues
                        - Maintain original strategy core
                        - Add missing justifications
                        - Simplify where possible""",
                        context=solution_draft
                    )
                    return repaired
                else:
                    return solution_draft
            except Exception as e:
                return f"STRATEGY {idx + 1} FAILED: {str(e)}"

        # Execute strategies in parallel
        strategy_results = await asyncio.gather(
            *[explore_strategy(strategy, i) for i, strategy in enumerate(strategy_list)]
        )

        # Step 3: Decomposition for Computational Pathways
        decomposition_plan = await self.decompose(
            instruction="""Decompose the original problem into minimal computational subproblems:
            - Prioritize subproblems solvable via symbolic manipulation or direct computation
            - Identify dependencies between subproblems
            - Flag any subproblems requiring numerical methods
            - Structure for sequential execution based on dependencies
            Return as list of subproblems with IDs and dependencies.""",
            context=""
        )

        # Execute decomposition chain
        subproblem_results = {}
        for subproblem in decomposition_plan:
            sub_id = subproblem['id']
            deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            
            # Wait for dependencies
            dep_context = "\n".join([f"Subproblem {dep}: {subproblem_results.get(dep, 'PENDING')}" for dep in deps if dep in subproblem_results])
            
            # Solve subproblem
            if "PENDING" in dep_context:
                continue  # Skip if dependencies not ready (shouldn't happen with proper ordering)
                
            sub_solution = await self.generate(
                instruction=f"""Solve subproblem: {subproblem['description']}
                Context from dependencies: {dep_context}
                
                Requirements:
                - Show all steps
                - Box final sub-result
                - Verify against original problem constraints""",
                context=dep_context
            )
            
            # Validate sub-solution
            validated_sub = await self.revise(
                instruction="Verify this sub-solution against original problem. Correct any errors.",
                context=sub_solution
            )
            subproblem_results[sub_id] = validated_sub

        # Step 4: Programmer Integration for Computation-Heavy Steps
        # Extract computational subproblems
        computational_steps = await self.generate(
            instruction=f"""From these subproblem results:
            {str(subproblem_results)}
            
            Identify which steps require precise computation (equation solving, summation, etc.).
            For each, generate exact Python code specifications including:
            - Required libraries
            - Input parameters
            - Expected output format
            - Validation checks""",
            context=str(subproblem_results)
        )

        # Execute computational steps
        computational_results = {}
        if "NO COMPUTATIONAL STEPS" not in computational_steps.upper():
            code_specs = await self.generate(
                instruction=f"""Convert these computational specifications into executable Python code blocks:
                {computational_steps}
                
                Requirements:
                - Include all necessary imports
                - Add validation assertions
                - Return results in specified format
                - Handle edge cases""",
                context=computational_steps
            )
            
            try:
                comp_result = await self.programmer(
                    instruction="Execute the generated code and return results.",
                    context=code_specs,
                    max_retries=3
                )
                computational_results['main'] = comp_result
            except Exception as e:
                computational_results['error'] = str(e)

        # Step 5: Ensemble Synthesis
        all_contexts = strategy_results + [str(subproblem_results), str(computational_results)]
        
        final_answer = await self.ensemble(
            instruction="""Synthesize all solution paths and computational results:
            1. Cross-validate all proposed answers.
            2. Identify consensus or most rigorous derivation.
            3. Extract final integer answer between 000-999.
            4. If conflict, select path with strongest validation.
            5. Format FINAL ANSWER as: \\boxed{XXX} where XXX is the integer.
            
            CRITICAL: The answer MUST be an integer between 000 and 999. Verify this constraint.""",
            contexts_list=all_contexts
        )

        # Step 6: Final Validation and Formatting
        verified_answer = await self.revise(
            instruction="""Final validation:
            - Confirm answer is integer 000-999
            - Verify against original problem statement
            - Check for calculation errors
            - Ensure proper \\boxed{} formatting
            If any issue, correct immediately.""",
            context=final_answer
        )

        # Extract boxed answer
        match = re.search(r'\\boxed\{(\d{3})\}', verified_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any 3-digit number
            numbers = re.findall(r'\b\d{3}\b', verified_answer)
            if numbers:
                return numbers[0]
            else:
                return "000"  # Ultimate fallback