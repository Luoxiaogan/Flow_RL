# Workflow ID: limr_48_0
# Benchmark: limr
# Data Indices: [168, 27]

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

        # STEP 1: META-CLASSIFICATION - Understand problem type, complexity, and strategies
        classification = await self.generate(
            instruction="""Perform a deep diagnostic analysis of this mathematical problem:

1. CLASSIFY the primary domain (Geometry, Number Theory, Combinatorics, Algebra, Probability, Optimization, Sequences, or Hybrid).
2. IDENTIFY key mathematical objects: equations, inequalities, sets, functions, geometric figures, etc.
3. ASSESS complexity on scale 1-5 (1=trivial, 5=extremely complex) based on:
   - Number of variables/constraints
   - Non-linearity or transcendental elements
   - Required proof depth or insight
   - Multi-step dependencies
4. LIST 2-3 viable solution strategies (e.g., "Coordinate Geometry + Integration", "Combinatorial Enumeration + Probability", "Modular Arithmetic + Diophantine Analysis").
5. FLAG any potential pitfalls or non-obvious insights needed.

Output in this structured format:
DOMAIN: [domain]
COMPLEXITY: [1-5]
STRATEGIES: 
- [Strategy 1]
- [Strategy 2]
- [Strategy 3]
PITFALLS: [pitfalls]
KEY_OBJECTS: [objects]""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING - Simple vs Complex handling
        complexity_match = re.search(r'COMPLEXITY:\s*([1-5])', classification)
        complexity = int(complexity_match.group(1)) if complexity_match else 3

        if complexity <= 2:
            # Simple problem - direct solve with verification
            direct_solution = await self.generate(
                instruction="""Solve this problem directly with minimal steps. Show all work clearly. Final answer must be an integer between 000 and 999. Verify your answer satisfies all constraints.""",
                context=classification
            )
            
            # Adversarial revision
            verified_solution = await self.revise(
                instruction="""Critically examine this solution as if you were its opponent. Find any logical gaps, calculation errors, or violated constraints. If none exist, strengthen the argument with additional verification steps. Final output must be a self-contained, bulletproof solution ending with the integer answer.""",
                context=direct_solution
            )
            
            # Extract final answer
            final_answer = await self.generate(
                instruction="""Extract ONLY the final integer answer (000-999) from this solution. If multiple answers exist, select the one that best satisfies all constraints. If no valid answer, output 'ERROR'. No explanation.""",
                context=verified_solution
            )
            
            return final_answer.strip()

        else:
            # Complex problem - parallel strategy exploration
            # Extract strategies from classification
            strategies_text = re.search(r'STRATEGIES:\s*(.*?)(?:PITFALLS:|$)', classification, re.DOTALL)
            strategies = []
            if strategies_text:
                strategy_lines = strategies_text.group(1).strip().split('\n')
                strategies = [s.strip('- ').strip() for s in strategy_lines if s.strip('- ').strip()]

            if len(strategies) < 2:
                strategies = [
                    "Analytical/Mathematical Proof Approach",
                    "Computational/Algorithmic Approach",
                    "Geometric/Visual Reasoning Approach"
                ][:3]

            # STEP 3: PARALLEL STRATEGY EXECUTION
            async def execute_strategy(strategy_desc, index):
                try:
                    # Generate initial solution attempt
                    solution_attempt = await self.generate(
                        instruction=f"""Develop a complete solution using this strategy: {strategy_desc}

Guidelines:
- Break into clear, logical steps
- Show all mathematical work
- Justify non-obvious insights
- Handle edge cases
- Final answer must be integer 000-999

If this strategy proves unworkable, explain why and attempt an alternative approach.""",
                        context=classification
                    )
                    
                    # Adversarial revision
                    refined_attempt = await self.revise(
                        instruction=f"""Assume this solution contains a critical error. Find it. If no error exists, strengthen the solution by:
1. Adding missing verification steps
2. Providing alternative derivation
3. Checking boundary conditions
4. Ensuring answer is integer 000-999

Output the corrected/improved solution.""",
                        context=solution_attempt
                    )
                    
                    # Computational verification if applicable
                    if any(kw in strategy_desc.lower() for kw in ['compute', 'algorithm', 'program', 'count', 'calculate']):
                        try:
                            code_verification = await self.programmer(
                                instruction=f"""Generate Python code to computationally verify the solution. Use sympy, numpy, or standard library. The code must:
- Reproduce the problem constraints exactly
- Compute the answer independently
- Output only the integer result (000-999)
- Include error checking

If computation is infeasible, return 'NOT_COMPUTABLE'.""",
                                context=refined_attempt,
                                max_retries=2
                            )
                            
                            # Combine analytical and computational results
                            combined_result = await self.generate(
                                instruction="""Synthesize the analytical solution and computational verification:
- If they agree, present the unified answer
- If they disagree, explain the discrepancy and determine which is correct
- Final output must be a single integer 000-999""",
                                context=f"ANALYTICAL: {refined_attempt}\n\nCOMPUTATIONAL: {code_verification}"
                            )
                            return combined_result
                        except Exception:
                            pass
                    
                    return refined_attempt
                except Exception as e:
                    return f"STRATEGY_FAILED: {strategy_desc} - {str(e)}"

            # Execute all strategies in parallel
            strategy_tasks = [execute_strategy(strategy, i) for i, strategy in enumerate(strategies)]
            strategy_results = await asyncio.gather(*strategy_tasks, return_exceptions=True)

            # Filter out failures
            valid_results = []
            for result in strategy_results:
                if isinstance(result, Exception):
                    continue
                if isinstance(result, str) and not result.startswith("STRATEGY_FAILED"):
                    valid_results.append(result)

            if not valid_results:
                # Fallback: direct solve
                fallback = await self.generate(
                    instruction="Solve this problem using any viable method. Show all work. Final answer must be integer 000-999.",
                    context=classification
                )
                valid_results = [fallback]

            # STEP 4: ENSEMBLE - Cross-validate and select best answer
            final_synthesis = await self.ensemble(
                instruction="""You are given multiple solution attempts for the same mathematical problem. Your task:

1. COMPARE all solutions for consistency in final answer.
2. If all agree, select that answer.
3. If they disagree:
   - Identify which solution has the most rigorous verification
   - Check which answer satisfies all problem constraints
   - Prefer computational verification when available
   - Select the most plausible integer answer (000-999)
4. OUTPUT ONLY the final integer answer. No explanation.

CRITICAL: The answer must be an integer between 000 and 999. If no consensus, pick the answer that appears most frequently or is best justified.""",
                contexts_list=valid_results
            )

            # STEP 5: FINAL SANITY CHECK
            sanity_checked = await self.generate(
                instruction="""Perform final validation:
- Is this answer an integer between 000 and 999?
- Does it satisfy all problem constraints?
- Is it mathematically plausible? (e.g., area > 0, probability ≤ 1)

If valid, output the integer. If invalid, output 'REJECTED' and the system will retry.

ANSWER TO VALIDATE: """ + final_synthesis,
                context=classification
            )

            # Extract clean answer
            clean_answer = await self.generate(
                instruction="Extract ONLY the final integer answer (000-999) from this text. If 'REJECTED' or invalid, output '000'. No explanation.",
                context=sanity_checked
            )

            return clean_answer.strip()