# Workflow ID: limr_22_0
# Benchmark: limr
# Data Indices: [258, 123]

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
        import json
        
        # PHASE 1: META-ANALYSIS - Understand problem type and strategy space
        meta_analysis = await self.generate(
            instruction="""Perform deep problem classification and strategy mapping:
            1. Identify primary mathematical domain (geometry, number theory, combinatorics, algebra, optimization)
            2. Detect secondary domains that may be involved
            3. List 3-5 potential solution approaches with their mathematical foundations
            4. Flag any non-obvious insights or transformations that might be required
            5. Identify potential pitfalls or common mistakes for this problem type
            6. Suggest verification methods for final answer
            Format as structured JSON with keys: domain, approaches, insights, pitfalls, verification""",
            context=""
        )
        
        # PHASE 2: PARALLEL STRATEGY EXPLORATION - Diamond Pattern
        # Generate 3 independent solution attempts using different approaches
        strategy_instructions = [
            """Pursue a geometric/visual approach:
            - Construct coordinate systems or diagrams if applicable
            - Use area/volume models for probability problems
            - Apply similarity, congruence, or proportionality principles
            - Derive equations from geometric constraints
            Show all steps and justify each transformation.""",
            
            """Pursue an algebraic/formal approach:
            - Define variables and constraints precisely
            - Set up equations or inequalities
            - Apply algebraic manipulations, substitutions, or transformations
            - Solve symbolically before numerical evaluation
            Show complete derivation with verification at each step.""",
            
            """Pursue a combinatorial/probabilistic approach:
            - Identify sample spaces and events
            - Apply counting principles, permutations, combinations
            - Use probability rules, expected values, or generating functions
            - Consider edge cases and boundary conditions
            Show combinatorial reasoning with clear justification."""
        ]
        
        # Execute parallel strategy branches with internal validation loops
        async def execute_strategy(strategy_instruction, branch_id):
            # Initial solution attempt
            solution = await self.generate(
                instruction=f"""{strategy_instruction}
                
                IMPORTANT: If you encounter a dead end or inconsistency, 
                explicitly state 'DEAD END DETECTED' and explain why this approach fails.
                Otherwise, proceed to full solution.""",
                context=meta_analysis
            )
            
            # Internal validation loop (max 2 iterations)
            for validation_round in range(2):
                validation = await self.generate(
                    instruction=f"""Critically validate this solution attempt:
                    1. Check for logical consistency and mathematical errors
                    2. Verify dimensional analysis and unit consistency
                    3. Test boundary conditions and edge cases
                    4. Confirm answer format matches requirements (integer 000-999)
                    5. If errors found, suggest specific corrections
                    
                    If solution is valid, respond with 'VALIDATED'.
                    If errors found, respond with 'ERROR: [description]'""",
                    context=solution
                )
                
                if "VALIDATED" in validation:
                    break
                elif "DEAD END" in solution or "ERROR" in validation:
                    # Generate diagnostic report instead of continuing
                    solution = await self.generate(
                        instruction=f"""Generate diagnostic report for failed approach:
                        - Why this strategy failed
                        - What mathematical insight was missing
                        - Alternative directions that might work
                        - Lessons learned for ensemble phase""",
                        context=f"Original attempt: {solution}\nValidation: {validation}"
                    )
                    break
                else:
                    # Revise and continue
                    solution = await self.revise(
                        instruction=f"""Correct all errors identified in validation:
                        Validation feedback: {validation}
                        Maintain mathematical rigor and show corrected steps.""",
                        context=solution
                    )
            
            return {
                "branch_id": branch_id,
                "strategy": strategy_instruction[:50] + "...",
                "solution": solution,
                "validation_status": "VALIDATED" if "VALIDATED" in validation else "FAILED"
            }
        
        # Run parallel strategy branches
        strategy_results = await asyncio.gather(
            execute_strategy(strategy_instructions[0], "geo"),
            execute_strategy(strategy_instructions[1], "alg"),
            execute_strategy(strategy_instructions[2], "comb")
        )
        
        # Extract just the solution texts for ensemble
        solution_texts = [result["solution"] for result in strategy_results]
        
        # PHASE 3: ENSEMBLE SYNTHESIS - Combine best elements from all branches
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a complete, correct solution by combining the strongest elements from all attempts:
            1. Identify which branch(es) correctly identified the core mathematical model
            2. Extract accurate sub-solutions from each branch (even if overall branch failed)
            3. Resolve contradictions between branches by mathematical verification
            4. Construct a unified solution path that incorporates the best insights
            5. Ensure all steps are mathematically rigorous and complete
            6. Format final answer as integer between 000-999 as required
            
            If all branches have significant flaws, propose a radically different approach 
            leveraging insights from the meta-analysis about non-obvious transformations.""",
            contexts_list=solution_texts
        )
        
        # PHASE 4: STRUCTURED DECOMPOSITION - Break synthesized solution into verifiable steps
        decomposition = await self.decompose(
            instruction="""Decompose the synthesized solution into atomic, verifiable steps:
            - Each step should be independently checkable
            - Specify dependencies between steps
            - Include validation criteria for each step
            - Ensure final step produces integer answer 000-999
            - Steps should follow logical progression from given information to final answer""",
            context=synthesized_solution
        )
        
        # PHASE 5: STEP-BY-STEP VALIDATION - Verify each subproblem
        async def solve_subproblem(subproblem):
            # Generate solution for this subproblem
            sub_solution = await self.generate(
                instruction=f"""Solve this specific subproblem with extreme precision:
                {subproblem['description']}
                
                Show all work, justify each step, and verify against dependencies:
                Dependencies: {subproblem.get('dependencies', 'None')}
                
                Final output for this subproblem must be clearly stated.""",
                context=synthesized_solution
            )
            
            # Validate with programmer if involves calculation
            if any(term in subproblem['description'].lower() for term in ['calculate', 'compute', 'find value', 'solve for']):
                try:
                    code_validation = await self.programmer(
                        instruction=f"""Generate Python code to verify the calculation in this subproblem:
                        {subproblem['description']}
                        
                        The code should:
                        1. Implement the mathematical operation described
                        2. Output the result
                        3. Include assertions to verify correctness
                        4. Handle edge cases mentioned in dependencies""",
                        context=sub_solution,
                        max_retries=2
                    )
                    # Append code validation to sub_solution
                    sub_solution += f"\n\nPROGRAMMER VALIDATION:\n{code_validation}"
                except Exception as e:
                    # If code fails, continue with manual validation
                    pass
            
            return {
                "id": subproblem["id"],
                "solution": sub_solution
            }
        
        # Solve subproblems respecting dependencies
        subproblem_solutions = {}
        for subproblem in decomposition:
            # Wait for dependencies if any
            if subproblem.get('dependencies'):
                dep_ids = [dep.strip() for dep in subproblem['dependencies'].split(',')]
                # In a full implementation, we'd wait for these dependencies
                # For simplicity, we'll proceed sequentially (dependencies are ordered)
                pass
            
            result = await solve_subproblem(subproblem)
            subproblem_solutions[subproblem["id"]] = result["solution"]
        
        # PHASE 6: FINAL SYNTHESIS AND ANSWER EXTRACTION
        final_context = "\n\n".join([
            f"Subproblem {id}: {solution}" 
            for id, solution in subproblem_solutions.items()
        ])
        
        final_answer = await self.generate(
            instruction="""Extract the final integer answer (000-999) from the complete solution:
            1. Review all subproblem solutions and synthesized solution
            2. Identify the final numerical result
            3. Ensure it's formatted as a 3-digit integer (pad with leading zeros if needed)
            4. If answer is fractional, multiply by appropriate factor to get integer
            5. If answer is irrational, identify the integer component requested
            6. Output ONLY the 3-digit integer, nothing else
            
            Example outputs: 042, 123, 999""",
            context=f"SYNTHESIZED SOLUTION:\n{synthesized_solution}\n\nSUBPROBLEM SOLUTIONS:\n{final_context}"
        )
        
        # Final validation: ensure answer is 3-digit integer
        try:
            answer_int = int(final_answer.strip())
            if 0 <= answer_int <= 999:
                final_answer = f"{answer_int:03d}"  # Pad to 3 digits
            else:
                # Fallback: extract first 3-digit number from synthesized solution
                final_answer = await self.generate(
                    instruction="Extract any 3-digit integer (000-999) mentioned in the solution as the answer",
                    context=synthesized_solution
                )
        except:
            # Last resort: return first 3 digits from synthesized solution
            digits = ''.join(filter(str.isdigit, synthesized_solution))
            final_answer = digits[:3].zfill(3) if len(digits) >= 3 else "000"
        
        return final_answer