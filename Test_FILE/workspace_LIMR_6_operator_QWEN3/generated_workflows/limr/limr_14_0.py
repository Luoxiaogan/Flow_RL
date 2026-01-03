# Workflow ID: limr_14_0
# Benchmark: limr
# Data Indices: [20, 65]

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
        import json

        # STEP 1: CLASSIFY PROBLEM DOMAIN AND STRUCTURE
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this mathematical problem. Identify:
            1. Primary mathematical domain (geometry, number theory, algebra, combinatorics, probability, etc.)
            2. Required answer format (integer, fraction, radical expression, etc.) and constraints (e.g., 000-999)
            3. Key entities: variables, constants, geometric objects, functions, sequences
            4. Relationships and constraints between entities
            5. Potential solution strategies ranked by applicability
            6. Known theorems or identities likely to be relevant
            Output as a structured JSON with keys: domain, answer_format, entities, constraints, strategies, theorems""",
            context=""
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION GUIDED BY CLASSIFICATION
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem into minimal solvable subproblems using the classification:
            Classification: {classification}
            
            Guidelines:
            - Each subproblem should be independently solvable or depend only on earlier subproblems
            - Include computational, theoretical, and verification subproblems
            - For geometry: consider coordinate, synthetic, and vector approaches
            - For algebra: consider substitution, symmetry, and transformation paths
            - For combinatorics: consider counting, recursion, and generating function paths
            - Always include a 'sanity check' subproblem for final validation
            - Output subproblems with clear dependencies and mathematical scope""",
            context=classification
        )

        # STEP 3: PARALLEL SOLUTION PATH GENERATION
        async def solve_subproblem(sub):
            try:
                # Generate initial solution attempt
                attempt = await self.generate(
                    instruction=f"""Solve subproblem: {sub['description']}
                    Classification context: {classification}
                    Dependencies (if any): {sub.get('dependencies', 'none')}
                    
                    Requirements:
                    - Show all mathematical steps
                    - Justify each transformation or theorem used
                    - Maintain precision (no approximations)
                    - If computational, prepare for code implementation
                    - Flag any assumptions made""",
                    context=""
                )
                
                # Self-validate the attempt
                validation = await self.generate(
                    instruction=f"""Critically validate this solution attempt:
                    Attempt: {attempt}
                    
                    Check for:
                    - Logical consistency
                    - Adherence to problem constraints
                    - Mathematical rigor (no skipped steps)
                    - Dimensional/numerical plausibility
                    - Alignment with classification context
                    Output validation report with 'PASSED' or 'FAILED' and specific issues""",
                    context=attempt
                )
                
                # Revise if validation fails
                if "FAILED" in validation:
                    revised = await self.revise(
                        instruction=f"""Revise solution based on validation feedback:
                        Validation: {validation}
                        Original attempt: {attempt}
                        
                        Requirements:
                        - Address all identified issues
                        - Maintain mathematical precision
                        - Add missing justifications
                        - Consider alternative approaches if original is flawed""",
                        context=attempt
                    )
                    return revised
                return attempt
            except Exception as e:
                return f"ERROR in subproblem {sub['id']}: {str(e)}"

        # Execute all subproblems in parallel
        subproblem_results = await asyncio.gather(
            *[solve_subproblem(sub) for sub in decomposition]
        )

        # Create mapping of subproblem IDs to results
        results_map = {decomposition[i]['id']: subproblem_results[i] for i in range(len(decomposition))}

        # STEP 4: SYNTHESIZE RESULTS WITH DEPENDENCY RESOLUTION
        synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in results_map.items()])
        
        synthesized = await self.generate(
            instruction=f"""Synthesize final solution from subproblem results:
            Subproblem Results: {synthesis_context}
            Classification: {classification}
            
            Steps:
            1. Resolve dependencies: ensure results used in later subproblems match earlier outputs
            2. Combine partial results into complete solution
            3. Verify consistency across all subproblems
            4. Simplify final expression to required format
            5. Extract final answer as integer 000-999 as specified
            6. Document any remaining uncertainties or assumptions""",
            context=synthesis_context
        )

        # STEP 5: ADVERSARIAL VALIDATION AND FORMATTING
        final_validation = await self.generate(
            instruction=f"""Perform adversarial validation of synthesized solution:
            Solution: {synthesized}
            Classification: {classification}
            
            Validation checklist:
            - Does the answer format match problem requirements (e.g., a+b+c for fraction form)?
            - Is the answer within 000-999 range?
            - Are all mathematical steps reversible and justified?
            - Are there any hidden assumptions that violate problem constraints?
            - Does dimensional analysis hold (e.g., areas positive, probabilities 0-1)?
            - Cross-check with alternative approach if time permits
            
            Output: 'VALID' or 'INVALID' followed by detailed justification""",
            context=synthesized
        )

        # Conditional branch based on validation
        if "INVALID" in final_validation:
            # Generate alternative approach
            alternative = await self.generate(
                instruction=f"""Generate alternative solution approach given validation failure:
                Original solution: {synthesized}
                Validation issues: {final_validation}
                Classification: {classification}
                
                Requirements:
                - Choose fundamentally different mathematical approach
                - Avoid assumptions that led to previous failure
                - Prioritize computational verification if theoretical path failed
                - Output complete alternative solution""",
                context=synthesized
            )
            final_answer = alternative
        else:
            final_answer = synthesized

        # STEP 6: FINAL FORMATTING AND EXTRACTION
        formatted_answer = await self.revise(
            instruction=f"""Extract and format final answer as required:
            Current solution: {final_answer}
            Classification: {classification}
            
            Formatting rules:
            - Extract only the final integer answer between 000 and 999
            - If answer is in form a+b+c, compute the sum
            - Remove all explanatory text, show only the number
            - Ensure no units or additional characters
            - If multiple candidates, select the one that passed validation
            - Output as exactly three digits (e.g., 042 for 42)""",
            context=final_answer
        )

        # Extract numeric answer using regex as final safeguard
        import re
        match = re.search(r'\b(\d{1,3})\b', formatted_answer)
        if match:
            answer = int(match.group(1))
            # Ensure three-digit format
            return f"{answer:03d}"
        else:
            # Fallback: return first three digits found or 000
            digits = re.findall(r'\d', formatted_answer)
            if len(digits) >= 3:
                return ''.join(digits[:3])
            elif len(digits) > 0:
                return ''.join(digits).zfill(3)
            else:
                return "000"