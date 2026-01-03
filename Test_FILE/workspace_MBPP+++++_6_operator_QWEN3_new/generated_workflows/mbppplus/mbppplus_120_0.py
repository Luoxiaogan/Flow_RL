# Workflow ID: mbppplus_120_0
# Benchmark: mbppplus
# Data Indices: [249, 283]

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

        # Phase 1: Problem Analysis and Strategy Generation (Parallel Fork)
        analysis_prompts = [
            """Analyze the problem and generate a mathematical/logical solution strategy.
            Steps:
            1. Identify input types and constraints.
            2. State the core logical/mathematical rule needed.
            3. Outline step-by-step reasoning without code.
            4. Highlight edge cases (empty, zero, negative, boundaries).
            5. Propose validation test cases.
            Be precise and rigorous.""",
            
            """Analyze the problem and generate an algorithmic/data-structure solution strategy.
            Steps:
            1. Identify if loops, conditionals, or data transformations are needed.
            2. Propose pseudo-code logic.
            3. Consider time/space complexity.
            4. Identify failure modes.
            5. Suggest alternative approaches.
            Focus on computational efficiency and correctness."""
        ]

        strategy_analyses = await asyncio.gather(
            *[self.generate(instruction=prompt, context="") for prompt in analysis_prompts]
        )

        # Phase 2: Hierarchical Decomposition for Each Strategy
        decomposition_tasks = []
        for i, analysis in enumerate(strategy_analyses):
            decomposition_tasks.append(
                self.decompose(
                    instruction=f"""Decompose this solution strategy into atomic, testable subproblems:
                    Strategy: {analysis}
                    
                    Requirements:
                    - Each subproblem must be independently solvable.
                    - Specify input/output for each.
                    - Order by dependency (use 'depends_on' field).
                    - Include edge case handling as separate subproblems if needed.
                    - Maximum 5 subproblems for simplicity.""",
                    context=analysis
                )
            )
        
        decomposed_strategies = await asyncio.gather(*decomposition_tasks)

        # Phase 3: Generate Solution Drafts and Code for Each Path
        solution_paths = []
        for i, (analysis, decomposition) in enumerate(zip(strategy_analyses, decomposed_strategies)):
            # Build context from decomposition
            decomposition_context = "\n".join([
                f"Step {step['id']}: {step['description']} (depends on: {step.get('dependencies', 'none')})"
                for step in decomposition
            ])
            
            # Generate integrated solution draft
            solution_draft = await self.generate(
                instruction=f"""Synthesize a complete solution from this decomposition:
                Original Analysis: {analysis}
                Decomposition:
                {decomposition_context}
                
                Requirements:
                - Write clear, step-by-step reasoning.
                - Explicitly handle all edge cases mentioned.
                - Format as: 'Step 1: ... Step 2: ... Conclusion: ...'
                - End with exact function signature and expected return type.""",
                context=decomposition_context
            )
            
            # Generate code from draft
            code_attempt = await self.programmer(
                instruction=f"""Generate Python code based EXACTLY on this reasoning:
                {solution_draft}
                
                Rules:
                - Use EXACT function name and parameters from problem.
                - Include necessary imports inside function if needed.
                - Handle all edge cases explicitly.
                - Return correct data type (bool, int, list, etc.).
                - No extra output or print statements.
                - Code must be self-contained and runnable.""",
                context=solution_draft,
                max_retries=2
            )
            
            solution_paths.append({
                'analysis': analysis,
                'decomposition': decomposition,
                'draft': solution_draft,
                'code': code_attempt
            })

        # Phase 4: Validate and Ensemble Best Solution
        validation_results = []
        for i, path in enumerate(solution_paths):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                Code: {path['code']}
                Against these requirements:
                1. Does it match the problem's logical intent?
                2. Does it handle all edge cases from analysis?
                3. Is return type correct?
                4. Any logical flaws or redundancies?
                5. Would it pass the example test cases?
                
                Respond in JSON format: {{"valid": true/false, "issues": ["list", "of", "issues"], "confidence": 0-10}}""",
                context=path['code']
            )
            validation_results.append(validation)

        # Ensemble selection
        best_solution = await self.ensemble(
            instruction="""Select the BEST solution based on:
            1. Correctness (must pass validation)
            2. Simplicity and clarity
            3. Edge case coverage
            4. Efficiency
            5. Adherence to problem constraints
            
            If multiple are valid, pick the most elegant.
            If none are fully valid, pick the one with fewest issues and highest confidence.
            Return ONLY the raw code block (no markdown, no explanation).""",
            contexts_list=[path['code'] for path in solution_paths]
        )

        # Phase 5: Edge Case Stress Test and Final Revision
        final_code = best_solution
        for iteration in range(3):  # Max 3 refinement loops
            edge_case_test = await self.generate(
                instruction=f"""Generate 5 extreme edge case tests for this code:
                {final_code}
                
                Include: empty inputs, zeros, negatives, maximum values, invalid types.
                Format as Python assert statements.""",
                context=final_code
            )
            
            # Extract assert statements
            assert_lines = re.findall(r'assert\s+.*', edge_case_test)
            if not assert_lines:
                break  # No testable assertions generated
                
            test_code = f"""
{final_code}

# Edge case tests
{chr(10).join(assert_lines)}
"""
            try:
                # Validate via programmer (which executes code)
                test_result = await self.programmer(
                    instruction="Execute these tests. If any fail, explain why. If all pass, say 'ALL TESTS PASS'.",
                    context=test_code,
                    max_retries=1
                )
                
                if "ALL TESTS PASS" in test_result:
                    break  # Success!
                else:
                    # Revise code based on failures
                    final_code = await self.revise(
                        instruction=f"""Fix the code to handle these failing edge cases:
                        Failure analysis: {test_result}
                        
                        Rules:
                        - Preserve original function signature.
                        - Fix ONLY the identified issues.
                        - Keep code as simple as possible.
                        - Return complete fixed code.""",
                        context=final_code
                    )
            except Exception:
                # If testing fails, break to avoid infinite loops
                break

        # Extract and return clean code block
        code_block_match = re.search(r'