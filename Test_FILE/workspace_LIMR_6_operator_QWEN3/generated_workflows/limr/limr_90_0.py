# Workflow ID: limr_90_0
# Benchmark: limr
# Data Indices: [22, 219]

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

        # PHASE 1: PROBLEM MAPPING & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify the problem domain (geometry, number theory, combinatorics, algebra, optimization, probability, etc.)
            2. Identify all given quantities, variables, and constraints (explicit and implicit)
            3. Determine the required output format (integer, fraction, decimal, etc.) and precision
            4. Extract key mathematical objects (functions, shapes, sequences, sets, etc.)
            5. Note any symmetries, invariants, or transformations that could simplify the problem
            6. Hypothesize 2-3 potential solution strategies with brief rationale for each
            Format your response as a structured markdown document with clear section headers.""",
            context=""
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems:
            - Each subproblem should be independently addressable with clear inputs and expected outputs
            - Specify dependencies between subproblems (which must be solved before others)
            - Include both computational and conceptual subproblems
            - For each, suggest the most appropriate solving method (analytical, computational, geometric, etc.)
            - Ensure the final subproblem produces the required answer format
            Return as a list of dictionaries with 'id', 'description', and 'dependencies' keys.""",
            context=problem_analysis
        )

        # PHASE 3: PARALLEL SOLUTION EXPLORATION
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            desc = subproblem['description']
            
            # Generate multiple solution approaches
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve subproblem {sub_id}: {desc}
                    Approach 1: Analytical/Algebraic Method
                    - Derive step-by-step symbolic solution
                    - Justify each transformation
                    - Handle edge cases explicitly""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""Solve subproblem {sub_id}: {desc}
                    Approach 2: Computational/Numeric Method
                    - Outline algorithmic steps
                    - Specify precision requirements
                    - Consider efficiency and edge cases""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""Solve subproblem {sub_id}: {desc}
                    Approach 3: Geometric/Visual or Combinatorial Method
                    - Use diagrams, counting principles, or spatial reasoning
                    - Leverage symmetries or combinatorial identities
                    - Provide intuitive explanation alongside formal solution""",
                    context=problem_analysis
                )
            )
            
            # Ensemble best solution for this subproblem
            best_solution = await self.ensemble(
                instruction=f"""Select and synthesize the best solution for subproblem {sub_id}:
                - Prioritize correctness and completeness
                - Favor methods that align with problem domain
                - Merge complementary insights from different approaches
                - Ensure output format matches requirements
                - Include verification step if applicable""",
                contexts_list=approaches
            )
            
            # Adversarial validation
            critique = await self.generate(
                instruction=f"""Critique this solution for subproblem {sub_id}:
                - Identify any logical gaps or assumptions
                - Check for calculation errors
                - Verify against constraints from problem analysis
                - Suggest improvements or alternatives""",
                context=best_solution
            )
            
            # Revise based on critique
            refined_solution = await self.revise(
                instruction=f"""Improve the solution using this critique:
                {critique}
                - Address all identified issues
                - Maintain clarity and precision
                - Preserve correct insights from original solution""",
                context=best_solution
            )
            
            return {
                'id': sub_id,
                'solution': refined_solution,
                'critique': critique
            }

        # Solve all subproblems in dependency order
        solved_subproblems = {}
        remaining = decomposition.copy()
        
        while remaining:
            # Find subproblems with satisfied dependencies
            ready = [
                sp for sp in remaining 
                if all(dep.strip() in solved_subproblems for dep in sp.get('dependencies', '').split(',') if dep.strip())
            ]
            
            if not ready:
                break  # Circular dependency or missing subproblem
            
            # Solve ready subproblems in parallel
            results = await asyncio.gather(*[solve_subproblem(sp) for sp in ready])
            
            # Store results
            for result in results:
                solved_subproblems[result['id']] = result['solution']
            
            # Remove solved subproblems
            remaining = [sp for sp in remaining if sp not in ready]

        # PHASE 4: SYNTHESIZE FINAL ANSWER
        all_solutions_text = "\n\n".join([
            f"Subproblem {sub_id}: {solution}" 
            for sub_id, solution in solved_subproblems.items()
        ])
        
        final_synthesis = await self.generate(
            instruction=f"""Synthesize all subproblem solutions into final answer:
            1. Integrate results from all subproblems in logical order
            2. Verify consistency between subproblem outputs
            3. Perform final calculation or derivation to produce required answer
            4. Format answer EXACTLY as specified in original problem (e.g., decimal to ten-thousandth, common fraction, integer 000-999)
            5. Include brief verification against original problem constraints
            6. Box the final answer using \\boxed{{}} notation""",
            context=f"Problem Analysis:\n{problem_analysis}\n\nSubproblem Solutions:\n{all_solutions_text}"
        )

        # PHASE 5: FINAL VALIDATION & FORMATTING
        validation = await self.generate(
            instruction="""Validate final answer:
            - Does it match required format? (integer 000-999, fraction, decimal precision, etc.)
            - Is it consistent with problem constraints?
            - Are units (if any) correct?
            - Does it pass dimensional analysis or sanity checks?
            If any issues, suggest correction. Otherwise, confirm 'VALID'.""",
            context=final_synthesis
        )
        
        if "VALID" not in validation.upper():
            final_answer = await self.revise(
                instruction=f"""Correct the answer based on validation feedback:
                {validation}
                Ensure final output is properly formatted and boxed.""",
                context=final_synthesis
            )
        else:
            final_answer = final_synthesis

        # Extract and return boxed answer
        box_pattern = r'\\boxed\{([^}]*)\}'
        matches = re.findall(box_pattern, final_answer)
        
        if matches:
            return matches[0].strip()
        else:
            # Fallback: return last 3 digits if integer expected
            digits = re.findall(r'\b\d{1,3}\b', final_answer)
            if digits:
                return digits[-1].zfill(3)
            else:
                return "000"  # Ultimate fallback