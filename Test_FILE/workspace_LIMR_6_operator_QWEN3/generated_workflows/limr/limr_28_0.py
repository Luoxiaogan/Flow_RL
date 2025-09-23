# Workflow ID: limr_28_0
# Benchmark: limr
# Data Indices: [114, 151]

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

        # PHASE 1: STRUCTURAL DECOMPOSITION & DIAGNOSIS
        decomposition = await self.decompose(
            instruction="""Perform deep structural analysis of this mathematical problem. Identify:
            1. The core mathematical domains involved (algebra, geometry, number theory, combinatorics, etc.)
            2. All variables, parameters, and unknowns
            3. Explicit and implicit constraints
            4. Governing principles or theorems that apply
            5. Potential transformation paths (substitutions, coordinate changes, symmetry exploitation, etc.)
            6. Edge cases or boundary conditions
            7. Expected answer format and type (integer, set, proof, etc.)
            Return as structured subproblems with dependencies, where each subproblem represents a reasoning track or strategy.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = []
        for i, subprob in enumerate(decomposition):
            strategy_tasks.append(
                self.generate(
                    instruction=f"""Develop a complete solution strategy for this mathematical subproblem:
                    {subprob['description']}
                    
                    Guidelines:
                    - If algebraic: show equation setup and solving steps
                    - If geometric: describe spatial reasoning or coordinate setup
                    - If combinatorial: specify counting principles or probability rules
                    - If number-theoretic: apply modular arithmetic, divisibility, or prime properties
                    - Include all necessary mathematical justifications
                    - Anticipate and address potential edge cases
                    - Structure output as: Strategy -> Steps -> Expected Outcome""",
                    context=""
                )
            )
        
        raw_strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: STRATEGY REFINEMENT & VALIDATION
        refined_strategies = []
        for strategy in raw_strategies:
            refined = await self.revise(
                instruction="""Critically review this mathematical strategy:
                1. Verify logical consistency and mathematical validity
                2. Check for missing cases or boundary conditions
                3. Ensure all constraints from original problem are respected
                4. Improve clarity and rigor of mathematical reasoning
                5. Add explicit verification steps where possible
                6. Flag any assumptions that need validation
                Return the improved, bulletproofed strategy.""",
                context=strategy
            )
            refined_strategies.append(refined)

        # PHASE 4: COMPUTATIONAL VERIFICATION (IF APPLICABLE)
        computational_checks = []
        for strategy in refined_strategies:
            # Dynamically decide if computation is needed
            needs_computation = await self.generate(
                instruction=f"""Determine if this strategy requires computational verification:
                {strategy}
                
                Return ONLY 'YES' or 'NO'.""",
                context=strategy
            )
            
            if "YES" in needs_computation.upper():
                code_result = await self.programmer(
                    instruction=f"""Implement and execute code to verify this mathematical strategy:
                    {strategy}
                    
                    Requirements:
                    - Use exact integer/rational arithmetic (no floats)
                    - Validate against all problem constraints
                    - Return ALL valid solutions, not just first found
                    - Handle edge cases explicitly
                    - Output must be parseable list of integers or clear 'no solution'""",
                    context=strategy,
                    max_retries=3
                )
                computational_checks.append(code_result)
            else:
                computational_checks.append("COMPUTATION_NOT_REQUIRED")

        # PHASE 5: SYNTHESIS & ENSEMBLE DECISION
        synthesis_contexts = []
        for i, (strategy, comp_check) in enumerate(zip(refined_strategies, computational_checks)):
            if comp_check != "COMPUTATION_NOT_REQUIRED":
                synthesis_contexts.append(
                    f"STRATEGY {i+1}:\n{strategy}\n\nCOMPUTATIONAL VERIFICATION:\n{comp_check}"
                )
            else:
                synthesis_contexts.append(
                    f"STRATEGY {i+1}:\n{strategy}\n\nVERIFICATION: Purely analytical - no computation needed"
                )

        final_answer = await self.ensemble(
            instruction="""Synthesize all solution strategies and their verifications to determine the correct answer.
            Criteria:
            1. Prefer strategies with computational verification when available
            2. Resolve contradictions by identifying flawed assumptions
            3. Combine complementary insights from multiple strategies
            4. Ensure final answer matches required format (integer 000-999, or list of integers)
            5. If multiple valid answers, list all in ascending order, comma-separated
            6. If no solution exists, state "NO SOLUTION"
            7. Final output must be ONLY the answer in required format, nothing else""",
            contexts_list=synthesis_contexts
        )

        # PHASE 6: FINAL VALIDATION & FORMATTING
        validated_answer = await self.revise(
            instruction="""Final validation of answer:
            1. Verify answer is integer(s) between 000-999 as required
            2. Check against original problem constraints
            3. Ensure proper formatting (comma-separated if multiple, ascending order)
            4. Remove any explanatory text - output ONLY the answer
            5. If answer is single integer, output as 3-digit with leading zeros if needed (e.g., 007)
            6. If multiple integers, separate by commas, no spaces, in ascending order (e.g., 123,456,789)""",
            context=final_answer
        )

        return validated_answer