# Workflow ID: limr_174_0
# Benchmark: limr
# Data Indices: [98, 227]

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
        
        # PHASE 1: META-ANALYSIS & DECOMPOSITION
        # Generate multiple decomposition strategies in parallel
        decomposition_strategies = await asyncio.gather(
            self.generate(
                instruction="""Perform deep problem decomposition with focus on algebraic structure:
                - Identify all variables, constraints, and relationships
                - Break into minimal solvable subproblems
                - Map dependencies between subproblems
                - Prioritize subproblems that unlock others
                Format as numbered list with dependency annotations.""",
                context=""
            ),
            self.generate(
                instruction="""Perform deep problem decomposition with focus on geometric/combinatorial structure:
                - Identify symmetries, invariants, or combinatorial patterns
                - Break into cases or scenarios
                - Map logical dependencies
                - Highlight potential 'key insight' subproblems
                Format as numbered list with dependency annotations.""",
                context=""
            ),
            self.generate(
                instruction="""Perform lateral decomposition - assume the problem is not what it seems:
                - What if this is a disguised version of a different problem type?
                - What counterintuitive approaches could work?
                - Identify 'trap' assumptions to avoid
                - Propose alternative interpretations
                Format as speculative bullet points.""",
                context=""
            )
        )
        
        # Synthesize best decomposition
        master_decomposition = await self.ensemble(
            instruction="""Synthesize a unified decomposition strategy:
            - Combine algebraic, structural, and lateral perspectives
            - Resolve conflicts by prioritizing mathematical rigor
            - Ensure all subproblems are well-defined and solvable
            - Create explicit dependency graph (use 'depends on: [id]' notation)
            - Output as JSON-like structure with keys: id, description, dependencies""",
            contexts_list=decomposition_strategies
        )
        
        # Extract and parse subproblems (simplified parsing for universal workflow)
        subproblems_raw = await self.generate(
            instruction="""Parse the following decomposition into structured subproblems:
            - Extract each subproblem with unique ID
            - List dependencies as comma-separated IDs
            - Preserve mathematical notation and constraints
            Output as Python list of dicts with keys: id, description, dependencies""",
            context=master_decomposition
        )
        
        # PHASE 2: DYNAMIC SUBPROBLEM SCHEDULING
        # Convert to actual subproblem objects (simulated parsing)
        subproblem_analysis = await self.generate(
            instruction="""Analyze subproblem dependencies and create execution schedule:
            - Identify independent subproblems (no dependencies) for parallel execution
            - Group dependent subproblems into sequential chains
            - Flag any circular dependencies or unsolvable subproblems
            - Propose execution order that minimizes blocking
            Output as: 1. Parallel groups (list of subproblem IDs), 2. Sequential chains""",
            context=subproblems_raw
        )
        
        # PHASE 3: PARALLEL SUBPROBLEM SOLVING
        # Solve independent subproblems in parallel
        parallel_subproblems = await self.generate(
            instruction="""Extract all subproblems that can be solved independently (no dependencies):
            - Return as list of subproblem objects with full descriptions
            - Include any relevant context from original problem
            Format as JSON array.""",
            context=subproblems_raw
        )
        
        # Generate solution attempts for each independent subproblem
        independent_solutions = []
        if "[]" not in parallel_subproblems:  # Check if there are parallel subproblems
            solution_attempts = await asyncio.gather(*[
                self.generate(
                    instruction=f"""Solve this subproblem with maximum rigor:
                    - Show all mathematical steps
                    - Consider multiple approaches if stuck
                    - Verify intermediate results
                    - Box final answer for this subproblem
                    Subproblem: {sp}""",
                    context=""
                ) for sp in [parallel_subproblems]  # Simplified for universal workflow
            ])
            independent_solutions.extend(solution_attempts)
        
        # PHASE 4: SEQUENTIAL CHAIN SOLVING WITH VALIDATION
        sequential_chain = await self.generate(
            instruction="""Extract sequential subproblem chain (dependent subproblems):
            - Order by dependency (earliest first)
            - Include full descriptions and required inputs from previous subproblems
            Format as ordered list.""",
            context=subproblems_raw
        )
        
        cumulative_context = "
".join(independent_solutions) if independent_solutions else ""
        sequential_solutions = []
        
        if "[]" not in sequential_chain:  # Check if there are sequential subproblems
            chain_steps = await self.generate(
                instruction="""Break sequential chain into individual steps with dependency resolution:
                - For each step, specify required inputs from previous steps
                - Generate solution strategy incorporating those inputs
                Output as numbered steps.""",
                context=sequential_chain
            )
            
            # Solve sequentially with validation at each step
            for step_num, step in enumerate(chain_steps.split('
'), 1):
                step_solution = await self.generate(
                    instruction=f"""Solve step {step_num} using previous results:
                    Previous context: {cumulative_context}
                    Current step: {step}
                    - Show complete derivation
                    - Verify consistency with previous results
                    - Flag any inconsistencies immediately""",
                    context=cumulative_context
                )
                
                # Validate this step before proceeding
                validation = await self.generate(
                    instruction=f"""Critically validate this solution step:
                    - Check mathematical correctness
                    - Verify consistency with problem constraints
                    - Look for edge cases or special conditions
                    - Suggest improvements if needed
                    Step: {step_solution}""",
                    context=step_solution
                )
                
                if "error" in validation.lower() or "inconsistency" in validation.lower():
                    step_solution = await self.revise(
                        instruction=f"""Fix identified issues: {validation}
                        Maintain mathematical rigor and consistency with previous steps.""",
                        context=step_solution
                    )
                
                sequential_solutions.append(step_solution)
                cumulative_context += f"
Step {step_num} Solution: {step_solution}"
        
        # PHASE 5: ADVERSARIAL VALIDATION & SYNTHESIS
        all_solutions_context = cumulative_context + "
" + "
".join(independent_solutions)
        
        # Generate multiple final answer candidates
        answer_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Derive final answer from complete solution context:
                - Synthesize all subproblem results
                - Ensure dimensional consistency
                - Format as integer 000-999
                - Show final verification step
                Context: {all_solutions_context}""",
                context=all_solutions_context
            ),
            self.programmer(
                instruction=f"""Compute final answer programmatically:
                - Translate mathematical solution into executable code
                - Handle edge cases and precision requirements
                - Output only the integer answer 000-999
                Context: {all_solutions_context}""",
                context=all_solutions_context
            ),
            self.generate(
                instruction=f"""Lateral verification - assume answer is wrong and try to disprove:
                - What counterexamples or edge cases would invalidate this?
                - What alternative interpretations could lead to different answers?
                - If no contradictions found, confirm answer
                Context: {all_solutions_context}""",
                context=all_solutions_context
            )
        )
        
        # Ensemble final answer with rigorous validation
        final_answer = await self.ensemble(
            instruction="""Select and refine the most reliable answer:
            - Compare mathematical derivation, computational result, and adversarial validation
            - Resolve discrepancies by prioritizing mathematical proof over computation
            - Ensure answer is integer between 000 and 999
            - Format as exactly three digits (e.g., '042' not '42')
            - If uncertain, trigger one final revision with all available context""",
            contexts_list=answer_candidates
        )
        
        # FINAL SANITY CHECK
        sanity_check = await self.generate(
            instruction=f"""Perform final sanity check:
            - Does answer format match requirements (exactly 3 digits)?
            - Does it satisfy original problem constraints?
            - Is it within reasonable bounds for the problem type?
            - If any doubt, revise immediately
            Final answer: {final_answer}""",
            context=final_answer
        )
        
        if "error" in sanity_check.lower() or "invalid" in sanity_check.lower():
            final_answer = await self.revise(
                instruction=f"""Correct based on sanity check: {sanity_check}
                Maintain three-digit format and mathematical correctness.""",
                context=final_answer
            )
        
        # Extract just the three-digit answer
        match = re.search(r'\b\d{3}\b', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: return first three digits found
            digits = re.findall(r'\d', final_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            else:
                return "000"  # Ultimate fallback