# Workflow ID: mbppplus_62_0
# Benchmark: mbppplus
# Data Indices: [81, 217]

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

        # Phase 1: Meta-Analysis & Classification
        analysis = await self.generate(
            instruction="""Perform deep problem analysis. Identify:
            1. Primary operation type (transform, filter, compute, validate, etc.)
            2. Input/output data types and structures (list, tuple, string, number, etc.)
            3. Mutability and order preservation requirements
            4. Explicit constraints from problem statement
            5. Implicit constraints (edge cases: empty, single element, duplicates, type mismatches, boundary values)
            6. Complexity level (low/medium/high) based on steps and subtlety
            7. Categories (e.g., string, math, list, logic)
            Output as structured JSON-like text with clear keys.""",
            context=""
        )

        # Phase 2: Conditional Strategy Selection
        complexity_check = await self.generate(
            instruction=f"""Based on this analysis:
            {analysis}
            
            Should this problem be decomposed into subproblems? Answer only 'yes' or 'no'.""",
            context=analysis
        )

        if "yes" in complexity_check.lower():
            # Phase 3B: Hierarchical Decomposition
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal, independent, solvable subproblems.
                Each subproblem should be self-contained and have clear input/output.
                Prioritize logical separation over granularity.""",
                context=analysis
            )
            
            # Solve subproblems in parallel
            sub_solutions = []
            for sub in subproblems:
                sub_desc = sub['description']
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem in isolation:
                    {sub_desc}
                    
                    Return only the core logic as a Python function snippet. Assume inputs are well-typed.
                    Handle edge cases relevant to this subproblem.""",
                    context=analysis
                )
                sub_solutions.append(sub_solution)
            
            # Synthesize final solution
            synthesis_context = "\n\n".join([f"Subproblem {i+1}: {sol}" for i, sol in enumerate(sub_solutions)])
            synthesized_code = await self.generate(
                instruction=f"""Synthesize a complete solution by integrating these subproblem solutions:
                {synthesis_context}
                
                Ensure type consistency, handle edge cases from analysis, and match expected function signature.
                Return only the complete function implementation with imports if needed.""",
                context=analysis
            )
            candidate_solutions = [synthesized_code]
            
        else:
            # Phase 3A: Direct Solve with Iterative Refinement
            candidate_solutions = []
            initial_code = await self.programmer(
                instruction=f"""Generate a Python function that solves the problem.
                Use the analysis for context: {analysis}
                Ensure correct function signature, handle edge cases, and return specified type.
                Prioritize clarity and correctness over cleverness.""",
                context=analysis,
                max_retries=1
            )
            candidate_solutions.append(initial_code)
            
            # Generate alternatives in parallel
            alt_approaches = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate an alternative implementation using different Python constructs (e.g., if used map, try list comprehension; if used loops, try recursion or built-ins).
                    Analysis context: {analysis}""",
                    context=analysis,
                    max_retries=1
                ),
                self.programmer(
                    instruction=f"""Generate a defensive implementation that explicitly checks for edge cases and type safety.
                    Analysis context: {analysis}""",
                    context=analysis,
                    max_retries=1
                )
            )
            candidate_solutions.extend(alt_approaches)
        
        # Phase 4: Ensemble Validation
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness (handles all edge cases from analysis)
            2. Readability and clarity
            3. Efficiency (avoid unnecessary operations)
            4. Adherence to function signature and return type
            5. Robustness (type handling, error prevention)
            Return only the selected code block.""",
            contexts_list=candidate_solutions
        )
        
        # Phase 5: Final Hardening
        final_code = await self.revise(
            instruction=f"""Harden this code for production:
            - Add explicit edge case handling if missing
            - Ensure return type matches specification exactly
            - Use appropriate data structures (list vs tuple vs set)
            - Optimize for clarity, not brevity
            - Preserve order if required
            - Do not change core logic unless fixing a flaw
            Analysis context: {analysis}
            Return only the complete, hardened function implementation.""",
            context=selected_solution
        )
        
        return final_code