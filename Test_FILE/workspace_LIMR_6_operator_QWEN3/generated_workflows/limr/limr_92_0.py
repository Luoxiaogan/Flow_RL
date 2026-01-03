# Workflow ID: limr_92_0
# Benchmark: limr
# Data Indices: [301, 129]

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

        # Step 1: Generate multiple high-level strategies
        strategy_prompt = """
        Propose three distinct, viable solution strategies for this mathematical problem.
        For each strategy:
        - Name the approach (e.g., "Algebraic Manipulation", "Modular Arithmetic", "Symmetry Exploitation")
        - Outline key steps and required mathematical tools
        - Estimate computational complexity and potential pitfalls
        - Rate feasibility on a scale of 1-10
        Prioritize strategies that leverage structural insights over brute force.
        Format each strategy as a numbered section with clear headings.
        """
        strategy1 = await self.generate(instruction=strategy_prompt, context="")
        strategy2 = await self.generate(instruction=strategy_prompt, context="")
        strategy3 = await self.generate(instruction=strategy_prompt, context="")

        # Step 2: Ensemble select best strategy
        best_strategy = await self.ensemble(
            instruction="""
            Evaluate the three proposed strategies and select the single most promising one.
            Criteria:
            1. Mathematical elegance and insight
            2. Computational feasibility
            3. Alignment with problem constraints
            4. Minimization of error-prone steps
            Justify your selection in detail, then output ONLY the selected strategy's full text.
            """,
            contexts_list=[strategy1, strategy2, strategy3]
        )

        # Step 3: Strategy-aware decomposition
        decomposition = await self.decompose(
            instruction=f"""
            Decompose the problem into subproblems based STRICTLY on the following strategy:
            {best_strategy}

            Requirements:
            - Maximum 6 subproblems
            - Explicit dependencies (e.g., "2 depends on 1")
            - Each subproblem must be solvable independently or with stated dependencies
            - Include verification steps as subproblems where appropriate
            Output as structured list of dictionaries with 'id', 'description', 'dependencies'.
            """,
            context=best_strategy
        )

        # Step 4: Solve subproblems with iterative validation
        subproblem_results = {}
        subproblem_attempts = {}

        for sub in decomposition:
            sub_id = sub['id']
            description = sub['description']
            deps = [d.strip() for d in sub.get('dependencies', '').split(',') if d.strip()]
            
            # Wait for dependencies
            if deps:
                await asyncio.gather(*[asyncio.sleep(0) for dep in deps if dep in subproblem_results])
                # In practice, you'd await actual dependency resolution; simplified here for clarity

            # Attempt subproblem up to 3 times
            for attempt in range(3):
                try:
                    # Generate solution approach for subproblem
                    sub_approach = await self.generate(
                        instruction=f"""
                        Solve this subproblem: "{description}"
                        Context from strategy: {best_strategy}
                        Previous attempts (if any): {subproblem_attempts.get(sub_id, [])}
                        Provide step-by-step reasoning, then box the final sub-result.
                        If computational, prepare for code generation.
                        """,
                        context=json.dumps(subproblem_results)
                    )

                    # If computational, use Programmer
                    if any(kw in description.lower() for kw in ['compute', 'calculate', 'sum', 'find value']):
                        code_result = await self.programmer(
                            instruction=f"""
                            Write Python code to solve: {description}
                            Use exact arithmetic. No floating point.
                            Validate input constraints. Handle edge cases.
                            Return only the final integer result.
                            """,
                            context=sub_approach,
                            max_retries=2
                        )
                        sub_result = code_result
                    else:
                        # Use Generate for non-computational subproblems
                        sub_result = await self.generate(
                            instruction=f"""
                            Finalize the solution to: "{description}"
                            Ensure logical rigor. Box the final answer.
                            """,
                            context=sub_approach
                        )

                    # Validate subproblem result
                    validation = await self.generate(
                        instruction=f"""
                        Critically validate this subproblem result:
                        Subproblem: {description}
                        Result: {sub_result}
                        Check for: off-by-one errors, domain violations, logical consistency.
                        If valid, output "VALID: [result]". If invalid, explain why.
                        """,
                        context=sub_approach
                    )

                    if "VALID:" in validation:
                        subproblem_results[sub_id] = validation.split("VALID:")[1].strip()
                        subproblem_attempts.setdefault(sub_id, []).append(sub_result)
                        break
                    else:
                        # Revise and retry
                        sub_approach = await self.revise(
                            instruction=f"""
                            Previous attempt failed validation: {validation}
                            Revise the solution approach. Address the specific issues raised.
                            """,
                            context=sub_approach
                        )
                        if attempt == 2:  # Last attempt
                            subproblem_results[sub_id] = f"ERROR: {validation}"
                except Exception as e:
                    if attempt == 2:
                        subproblem_results[sub_id] = f"EXCEPTION: {str(e)}"

        # Step 5: Synthesize final answer
        synthesis = await self.generate(
            instruction=f"""
            Synthesize a complete, coherent solution using these subproblem results:
            {json.dumps(subproblem_results, indent=2)}

            Steps:
            1. Weave sub-results into a logical narrative
            2. Fill any gaps with additional reasoning
            3. Derive the final answer (integer 000-999)
            4. Box the final answer as \boxed{{number}}

            Ensure no step is skipped. Verify arithmetic and logic.
            """,
            context=best_strategy
        )

        # Step 6: Generate alternative solution for verification
        alt_solution = await self.generate(
            instruction="""
            Solve the original problem from scratch using a completely different approach.
            Do not reference previous steps. Be concise but rigorous.
            Output only the final boxed answer.
            """,
            context=""
        )

        # Step 7: Ensemble reconcile and finalize
        final_answer = await self.ensemble(
            instruction="""
            Compare the two solutions:
            - Primary synthesis: includes step-by-step reasoning
            - Alternative solution: independent verification
            
            If they agree, output the answer.
            If they disagree, identify the error, reconcile, and output corrected answer.
            FINAL OUTPUT MUST BE A SINGLE INTEGER BETWEEN 0 AND 999.
            Format: \boxed{number}
            """,
            contexts_list=[synthesis, alt_solution]
        )

        # Step 8: Final validation and formatting
        validated_answer = await self.generate(
            instruction="""
            Extract the final integer answer from the following text.
            Verify it is an integer between 0 and 999 inclusive.
            If not, apply modulo 1000 or reinterpret as required by problem context.
            Output ONLY the integer, no text, no boxes.
            """,
            context=final_answer
        )

        return validated_answer.strip()