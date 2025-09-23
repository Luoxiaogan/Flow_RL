# Workflow ID: limr_121_0
# Benchmark: limr
# Data Indices: [162, 318]

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

        # STEP 1: Decompose and classify the problem
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal subproblems. For each:
            - Identify the mathematical domain (algebra, geometry, combinatorics, etc.)
            - Specify required techniques (induction, coordinate transform, modular arithmetic, etc.)
            - Note dependencies between subproblems
            - Flag if subproblem is computational (requires programmer) or theoretical
            - Identify potential edge cases or degenerate conditions
            Output structured subproblems with these annotations.""",
            context=""
        )

        # Summarize decomposition into a roadmap
        roadmap = await self.summarize(
            instruction="""Create a concise solution roadmap:
            - List subproblems in dependency order
            - Highlight key mathematical domains and techniques
            - Note computational vs theoretical subproblems
            - Flag critical constraints and edge cases
            Format as numbered list with domain tags.""",
            context=str(decomposition)
        )

        # STEP 2: Parallel solution generation with self-critique
        async def solve_subproblem(sub_desc, idx):
            # Generate initial solution
            attempt = await self.generate(
                instruction=f"""Solve this subproblem:
                {sub_desc}
                
                Strategy: Use domain-appropriate techniques. Show all steps. 
                If computational, describe algorithm before calculating.
                If theoretical, provide rigorous justification.
                Return complete reasoning and final answer.""",
                context=roadmap
            )
            
            # Self-critique the attempt
            critique = await self.revise(
                instruction="""Critically review this solution:
                - Check logical consistency and step validity
                - Verify alignment with original problem constraints
                - Test edge cases and boundary conditions
                - Identify any gaps or errors
                - If flawed, suggest specific corrections
                Return revised solution with critique notes.""",
                context=attempt
            )
            
            return critique

        # Launch parallel subproblem solving
        subproblem_tasks = [
            solve_subproblem(sub['description'], i) 
            for i, sub in enumerate(decomposition)
        ]
        sub_solutions = await asyncio.gather(*subproblem_tasks)

        # Summarize sub-solutions for ensemble
        solution_summaries = []
        for i, sol in enumerate(sub_solutions):
            summary = await self.summarize(
                instruction=f"""Summarize solution for subproblem {i+1}:
                - Key steps and reasoning
                - Final result
                - Confidence level (high/medium/low)
                - Remaining uncertainties
                Keep under 100 words.""",
                context=sol
            )
            solution_summaries.append(f"Subproblem {i+1}: {summary}")

        # STEP 3: Ensemble synthesis
        final_answer = await self.ensemble(
            instruction="""You are a mathematics olympiad grader. 
            Synthesize the subproblem solutions into a complete answer:
            - Ensure all dependencies are satisfied
            - Resolve any conflicts between sub-solutions
            - Verify final answer meets original problem requirements
            - If any sub-solution is low confidence, note it and propose verification
            - Return ONLY the final integer answer (000-999) or fraction if specified.
            - If uncertain, return 'RETRY' and explain why.""",
            contexts_list=solution_summaries
        )

        # STEP 4: Adaptive reframing if needed (Level 4 innovation)
        if "RETRY" in final_answer:
            for reframing_round in range(2):  # Max 2 reframes
                # Generate alternative representation
                reframe = await self.generate(
                    instruction=f"""Problem resists solution. Reframe fundamentally:
                    - Change mathematical representation (e.g., algebraic → geometric)
                    - Apply duality or transformation (e.g., complementary counting, coordinate shift)
                    - Use advanced technique (generating functions, invariants, extremal principle)
                    - Reformulate as optimization or existence problem
                    Return reframed problem statement and new solution strategy.""",
                    context=f"Original: {self.problem_text}\nPrevious attempts: {final_answer}"
                )
                
                # Redecompose and retry
                new_decomposition = await self.decompose(
                    instruction="""Decompose this reframed problem:
                    - Identify new subproblems and domains
                    - Note how this differs from original decomposition
                    - Specify novel techniques required""",
                    context=reframe
                )
                
                # Repeat parallel solving (simplified for brevity)
                new_sub_solutions = await asyncio.gather(*[
                    solve_subproblem(sub['description'], i)
                    for i, sub in enumerate(new_decomposition)
                ])
                
                new_summaries = [
                    await self.summarize(
                        instruction="Summarize key result and confidence",
                        context=sol
                    ) for sol in new_sub_solutions
                ]
                
                final_answer = await self.ensemble(
                    instruction="""Synthesize reframed solutions. Return final answer or 'RETRY'.
                    If answer is fractional, convert to required format (integer 000-999).""",
                    contexts_list=new_summaries
                )
                
                if "RETRY" not in final_answer:
                    break

        # STEP 5: Final verification and formatting
        verified_answer = await self.revise(
            instruction="""Final verification:
            - Ensure answer is integer 000-999 or specified fraction
            - Confirm no calculation errors
            - Validate against original problem constraints
            - If fraction, reduce to simplest form
            Return ONLY the final answer in required format.""",
            context=final_answer
        )

        return verified_answer