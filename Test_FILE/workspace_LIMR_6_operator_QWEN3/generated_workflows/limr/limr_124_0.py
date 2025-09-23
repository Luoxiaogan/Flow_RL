# Workflow ID: limr_124_0
# Benchmark: limr
# Data Indices: [207, 349]

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

        # PHASE 1: PARALLEL EXPLORATION
        # Generate three complementary analyses simultaneously
        exploration_tasks = [
            self.generate(
                instruction="""Perform deep structural decomposition:
                1. Identify all mathematical objects (sets, functions, geometric entities, sequences)
                2. Extract explicit and implicit constraints
                3. Map relationships between variables/entities
                4. Identify potential solution pathways (algebraic, combinatorial, geometric, etc.)
                5. Flag any ambiguities or edge cases requiring clarification
                Format as a structured markdown outline with clear section headers.""",
                context=""
            ),
            self.generate(
                instruction="""Classify problem domain and required techniques:
                - Primary domain (number theory, combinatorics, geometry, algebra, etc.)
                - Secondary domains involved
                - Required proof techniques or computational methods
                - Expected answer format and constraints (especially 000-999 integer requirement)
                - Known pitfalls or common mistakes for this problem type
                - Recommended verification strategies
                Present as a categorized bullet-point list with confidence scores for each classification.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all numerical constraints and boundary conditions:
                - List all explicit numbers, ranges, and inequalities
                - Infer implicit boundaries (e.g., digit constraints, prime ranges)
                - Identify optimization targets or extremal conditions
                - Note any modular arithmetic or divisibility requirements
                - Extract combinatorial parameters (n choose k, permutations, etc.)
                Format as a table with columns: Constraint, Type, Source (explicit/inferred), Impact on Solution""",
                context=""
            )
        ]
        
        structural_analysis, domain_classification, constraint_table = await asyncio.gather(*exploration_tasks)
        
        # Synthesize exploration results into unified problem map
        problem_map = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified problem-solving blueprint:
            1. Combine structural decomposition with domain classification to identify primary solution approach
            2. Integrate constraint table to define computational boundaries
            3. Resolve any conflicts between analyses
            4. Prioritize solution strategies based on confidence and feasibility
            5. Generate specific instructions for computational implementation
            Output format: 
            # PROBLEM BLUEPRINT
            ## Primary Approach: [domain] with [technique]
            ## Key Constraints: [bulleted list]
            ## Solution Strategy: [step-by-step plan]
            ## Verification Protocol: [how to validate answer]
            ## Edge Cases: [potential failure points]""",
            contexts_list=[structural_analysis, domain_classification, constraint_table]
        )

        # PHASE 2: PARALLEL SOLUTION ATTEMPTS
        # Attempt three different solution strategies simultaneously
        solution_tasks = [
            self.generate(
                instruction=f"""Develop analytical solution using mathematical derivation:
                Based on problem blueprint:
                {problem_map}
                
                Steps:
                1. Formulate equations or logical relationships
                2. Apply appropriate mathematical theorems or identities
                3. Perform algebraic manipulations step by step
                4. Solve for target variable/quantity
                5. Verify solution satisfies all constraints
                6. Format final answer as integer between 000-999
                Show all work with clear justification for each step.""",
                context=problem_map
            ),
            self.programmer(
                instruction=f"""Implement computational solution:
                Based on problem blueprint:
                {problem_map}
                
                Requirements:
                - Generate efficient Python code to compute exact answer
                - Handle edge cases identified in blueprint
                - Validate result is integer between 000-999
                - Include comprehensive comments explaining algorithm
                - Use appropriate data structures and algorithms for problem type
                - Test with sample inputs if applicable
                Return code and output in markdown code blocks.""",
                context=problem_map,
                max_retries=2
            ),
            self.generate(
                instruction=f"""Develop alternative solution via problem transformation:
                Based on problem blueprint:
                {problem_map}
                
                Strategy:
                1. Transform problem into different mathematical domain (e.g., geometry to algebra, combinatorics to recursion)
                2. Apply isomorphic mapping or duality principle
                3. Solve transformed problem
                4. Map solution back to original domain
                5. Verify equivalence with original constraints
                6. Format final answer as integer between 000-999
                Document transformation process and justification.""",
                context=problem_map
            )
        ]
        
        analytical_solution, computational_solution, transformed_solution = await asyncio.gather(*solution_tasks)
        
        # PHASE 3: VERIFICATION AND REFINEMENT
        # Extract numerical answers from each solution attempt
        answer_extraction = await self.ensemble(
            instruction="""Extract final numerical answers from all three solution attempts:
            - Identify the final integer answer in each solution (should be between 000-999)
            - Note any discrepancies between answers
            - Flag solutions that don't provide a clear integer answer
            - Assess confidence level for each extracted answer based on solution quality
            Format as JSON: {"analytical": {"answer": int, "confidence": float, "issues": list}, 
                           "computational": {"answer": int, "confidence": float, "issues": list}, 
                           "transformed": {"answer": int, "confidence": float, "issues": list}}""",
            contexts_list=[analytical_solution, computational_solution, transformed_solution]
        )

        # If consensus exists, return it. Otherwise, enter refinement loop.
        consensus_check = await self.generate(
            instruction=f"""Check for answer consensus and determine next steps:
            Based on extracted answers:
            {answer_extraction}
            
            Decision logic:
            - If all three answers match and are valid (000-999), return that answer
            - If two match and one differs, return the majority answer
            - If all differ or no valid answers, initiate refinement process
            - If any answer is outside 000-999 range, flag for revision
            Output format: "CONSENSUS: [answer]" or "REFINE: [reasons]" """,
            context=answer_extraction
        )

        if "CONSENSUS" in consensus_check:
            final_answer = consensus_check.split(":")[1].strip()
            return final_answer

        # REFINEMENT LOOP (up to 3 iterations)
        current_solutions = [analytical_solution, computational_solution, transformed_solution]
        for iteration in range(3):
            # Identify weakest solution for revision
            weakest_analysis = await self.generate(
                instruction=f"""Identify weakest solution and revision strategy:
                Based on extracted answers and solutions:
                {answer_extraction}
                {str(current_solutions)}
                
                Analysis:
                1. Which solution has lowest confidence or most issues?
                2. What specific errors or gaps need correction?
                3. What revision strategy would most likely fix these issues?
                4. Should we switch solution approaches entirely?
                Output format: "REVISE: [solution_type] because [reasons]. Strategy: [specific_revision_instructions]" """,
                context=answer_extraction
            )
            
            # Parse which solution to revise
            solution_type_to_revise = "analytical"
            if "computational" in weakest_analysis:
                solution_type_to_revise = "computational"
            elif "transformed" in weakest_analysis:
                solution_type_to_revise = "transformed"
            
            # Get revision instructions
            revision_instructions = weakest_analysis.split("Strategy:")[1].strip() if "Strategy:" in weakest_analysis else "Fix identified errors and improve solution quality"
            
            # Revise the weakest solution
            solution_index = ["analytical", "computational", "transformed"].index(solution_type_to_revise)
            if solution_type_to_revise == "computational":
                revised_solution = await self.programmer(
                    instruction=f"""Revise computational solution:
                    {revision_instructions}
                    
                    Original problem blueprint:
                    {problem_map}
                    
                    Previous solution attempt:
                    {current_solutions[solution_index]}""",
                    context=current_solutions[solution_index],
                    max_retries=2
                )
            else:
                revised_solution = await self.revise(
                    instruction=f"""Revise solution with focus on:
                    {revision_instructions}
                    
                    Ensure final answer is integer between 000-999.
                    Address all issues identified in previous analysis.
                    Improve clarity, correctness, and completeness.""",
                    context=current_solutions[solution_index]
                )
            
            # Update solutions list
            current_solutions[solution_index] = revised_solution
            
            # Re-extract answers
            answer_extraction = await self.ensemble(
                instruction="""Extract final numerical answers from all three solution attempts:
                - Identify the final integer answer in each solution (should be between 000-999)
                - Note any discrepancies between answers
                - Flag solutions that don't provide a clear integer answer
                - Assess confidence level for each extracted answer based on solution quality
                Format as JSON: {"analytical": {"answer": int, "confidence": float, "issues": list}, 
                               "computational": {"answer": int, "confidence": float, "issues": list}, 
                               "transformed": {"answer": int, "confidence": float, "issues": list}}""",
                contexts_list=current_solutions
            )
            
            # Check for consensus again
            consensus_check = await self.generate(
                instruction=f"""Check for answer consensus:
                Based on extracted answers:
                {answer_extraction}
                
                Decision logic:
                - If all three answers match and are valid (000-999), return that answer
                - If two match and one differs, return the majority answer
                - If all differ or no valid answers, continue refinement
                - If any answer is outside 000-999 range, flag for revision
                Output format: "CONSENSUS: [answer]" or "REFINE: [reasons]" """,
                context=answer_extraction
            )
            
            if "CONSENSUS" in consensus_check:
                final_answer = consensus_check.split(":")[1].strip()
                return final_answer

        # If still no consensus after 3 iterations, return highest confidence answer
        final_extraction = await self.generate(
            instruction=f"""Select best answer from final attempts:
            Based on extracted answers:
            {answer_extraction}
            
            Strategy:
            1. Select answer with highest confidence score
            2. If confidence scores are equal, prefer computational solution
            3. Ensure selected answer is integer between 000-999
            4. If no valid answers, return 000 as fallback
            Output format: "FINAL: [answer]" """,
            context=answer_extraction
        )
        
        final_answer = final_extraction.split(":")[1].strip() if "FINAL:" in final_extraction else "000"
        return final_answer