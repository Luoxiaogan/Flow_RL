# Workflow ID: limr_101_0
# Benchmark: limr
# Data Indices: [330, 264]

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
        import re
        
        # PHASE 1: META-ANALYSIS AND STRATEGY CLASSIFICATION
        meta_analysis = await self.generate(
            instruction="""Perform deep problem analysis with these objectives:
            1. Classify the problem type (algebra, combinatorics, number theory, geometry, etc.)
            2. Identify key mathematical structures (sequences, polynomials, geometric figures, etc.)
            3. Determine if solution requires: direct computation, pattern recognition, or conceptual insight
            4. Estimate complexity level (number of steps, sophistication of required techniques)
            5. Suggest 2-3 promising solution approaches with brief rationale for each
            6. Flag any potential pitfalls or common mistakes for this problem type
            7. Predict whether answer will be small (<100), medium (100-500), or large (>500)
            
            Format your response as a structured analysis with clear section headings.""",
            context=""
        )
        
        # Extract strategy classification for conditional branching
        strategy_analysis = await self.generate(
            instruction="""Based on the meta-analysis, classify this problem for workflow routing:
            - COMPUTATIONAL: Requires significant calculation or algorithmic solution
            - CONCEPTUAL: Relies on insight, pattern recognition, or mathematical transformation
            - STRUCTURAL: Needs decomposition into multiple interdependent subproblems
            - HYBRID: Requires combination of above approaches
            
            Also identify:
            - Primary mathematical domain (algebra, combinatorics, etc.)
            - Key techniques likely needed (modular arithmetic, generating functions, coordinate geometry, etc.)
            - Expected answer range (0-99, 100-499, 500-999)
            
            Return ONLY a JSON object with keys: "strategy", "domain", "techniques", "answer_range".""",
            context=meta_analysis
        )
        
        try:
            strategy_data = json.loads(strategy_analysis)
            strategy = strategy_data.get("strategy", "HYBRID").upper()
            domain = strategy_data.get("domain", "")
            techniques = strategy_data.get("techniques", [])
        except:
            # Fallback if JSON parsing fails
            strategy = "HYBRID"
            domain = ""
            techniques = []
        
        # PHASE 2: PARALLEL EXPLORATION - LAUNCH MULTIPLE APPROACHES SIMULTANEOUSLY
        # Each approach receives customized instructions based on meta-analysis
        
        # Approach 1: Computational/Algorithmic Solution
        computational_task = asyncio.create_task(
            self.programmer(
                instruction=f"""Develop a Python solution for this problem.
                Problem domain: {domain}
                Likely techniques: {', '.join(techniques) if techniques else 'various'}
                
                Guidelines:
                - If the problem involves sequences, consider generating functions or recurrence relations
                - For number theory problems, use modular arithmetic optimizations
                - For combinatorics, consider dynamic programming or combinatorial identities
                - Ensure code handles edge cases and validates intermediate results
                - Return only the final integer answer (000-999) as the last line of output
                - Include brief comments explaining key insights
                
                IMPORTANT: If direct computation seems infeasible (too large numbers, infinite sequences, etc.),
                focus on finding patterns or mathematical shortcuts instead.""",
                context=meta_analysis
            )
        )
        
        # Approach 2: Conceptual/Patter Recognition
        conceptual_task = asyncio.create_task(
            self.generate(
                instruction=f"""Solve this problem through conceptual insight and pattern recognition.
                Based on the meta-analysis, focus on: {domain} and techniques like {', '.join(techniques) if techniques else 'various'}.
                
                Strategy:
                1. Look for hidden patterns, symmetries, or mathematical transformations
                2. Consider alternative representations (binary, base conversion, generating functions, etc.)
                3. Identify invariants or conserved quantities
                4. Apply relevant mathematical theorems or competition problem-solving heuristics
                5. Show step-by-step reasoning leading to the final answer
                6. Express final answer as a 3-digit integer (000-999)
                
                Think like a math competition winner - elegant solutions often beat brute force.""",
                context=meta_analysis
            )
        )
        
        # Approach 3: Structural Decomposition (for multi-step problems)
        decomposition_task = asyncio.create_task(
            self.decompose(
                instruction=f"""Break this problem into minimal set of interdependent subproblems.
                Problem type: {strategy}
                Domain: {domain}
                
                Guidelines:
                - Identify atomic subproblems that can be solved independently
                - Specify dependencies between subproblems
                - For each subproblem, indicate whether it requires computation, insight, or both
                - Prioritize subproblems that might reveal key insights or patterns
                - Maximum 5 subproblems unless absolutely necessary
                
                Return structured list of subproblems with clear descriptions and dependencies.""",
                context=meta_analysis
            )
        )
        
        # Execute all approaches in parallel
        comp_result, concept_result, decomposition_result = await asyncio.gather(
            computational_task, 
            conceptual_task, 
            decomposition_task,
            return_exceptions=True
        )
        
        # Process decomposition result into executable steps if valid
        structural_approach = ""
        if isinstance(decomposition_result, list) and len(decomposition_result) > 0:
            # Execute the decomposition by solving each subproblem in dependency order
            solved_subproblems = {}
            for subproblem in decomposition_result:
                try:
                    sub_id = subproblem.get('id', '')
                    description = subproblem.get('description', '')
                    deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                    
                    # Wait for dependencies
                    dep_context = "\n".join([f"Subproblem {dep}: {solved_subproblems.get(dep, '')}" for dep in deps if dep in solved_subproblems])
                    
                    # Solve subproblem
                    sub_solution = await self.generate(
                        instruction=f"""Solve this subproblem as part of larger solution:
                        {description}
                        
                        Context from dependencies:
                        {dep_context}
                        
                        Provide clear, concise solution. If computational, show key steps.
                        Format final result as: "ANSWER: [result]" where result is a number or brief phrase.""",
                        context=meta_analysis
                    )
                    
                    solved_subproblems[sub_id] = sub_solution
                except Exception as e:
                    continue
            
            # Synthesize final answer from subproblems
            if solved_subproblems:
                structural_approach = await self.generate(
                    instruction="""Synthesize final answer from solved subproblems.
                    Combine insights and results from all subproblems to derive the final answer.
                    Show how subproblem solutions connect to form complete solution.
                    Final answer must be a 3-digit integer (000-999).""",
                    context="\n\n".join([f"Subproblem {k}: {v}" for k, v in solved_subproblems.items()])
                )
        
        # Collect all valid approaches for ensemble
        candidate_solutions = []
        for result in [comp_result, concept_result, structural_approach]:
            if isinstance(result, str) and len(result.strip()) > 0:
                candidate_solutions.append(result)
        
        # PHASE 3: SYNTHESIS AND VERIFICATION
        if len(candidate_solutions) == 0:
            # Fallback: comprehensive generate approach
            final_answer = await self.generate(
                instruction="""Solve this problem using any appropriate mathematical techniques.
                Show complete step-by-step reasoning.
                Final answer must be a 3-digit integer between 000 and 999.
                Double-check your work for calculation errors and logical consistency.""",
                context=meta_analysis
            )
        else:
            # Ensemble to select or synthesize best answer
            synthesized = await self.ensemble(
                instruction="""Evaluate and synthesize these candidate solutions:
                - Identify which solution(s) are mathematically correct and complete
                - Look for consensus among approaches
                - If solutions conflict, determine which is most rigorous and error-free
                - Synthesize insights from multiple approaches if they complement each other
                - Final output must be a single 3-digit integer (000-999)
                - If uncertain, apply additional verification steps before deciding
                
                Return ONLY the 3-digit integer answer (e.g., "123"), nothing else.""",
                contexts_list=candidate_solutions
            )
            
            # Verification loop - up to 3 iterations
            final_answer = synthesized
            for verification_round in range(3):
                verification = await self.generate(
                    instruction=f"""Critically verify this answer: {final_answer}
                    - Check for calculation errors
                    - Verify logical consistency with problem constraints
                    - Ensure answer format is correct (3-digit integer 000-999)
                    - Consider edge cases and boundary conditions
                    - If answer seems incorrect, suggest correction
                    
                    Return "VERIFIED" if answer is correct, or "ERROR: [explanation]" if not.""",
                    context=f"Original problem analysis: {meta_analysis}\n\nCandidate solutions: {'; '.join(candidate_solutions[:3])}"
                )
                
                if "VERIFIED" in verification.upper():
                    break
                elif "ERROR" in verification.upper():
                    # Try to correct the answer
                    corrected = await self.revise(
                        instruction=f"""Correct the answer based on this verification feedback:
                        {verification}
                        
                        Provide the corrected 3-digit integer answer (000-999).
                        Show brief reasoning for the correction.""",
                        context=final_answer
                    )
                    final_answer = corrected
                else:
                    # If verification is inconclusive, break to avoid infinite loop
                    break
        
        # Final extraction of 3-digit answer
        answer_extraction = await self.generate(
            instruction="""Extract the final 3-digit integer answer (000-999) from the following text.
            If multiple numbers appear, select the one that is most likely the answer based on context.
            If no clear answer, return "000".
            
            Return ONLY the 3-digit number, nothing else.""",
            context=final_answer
        )
        
        # Clean and validate final answer
        # Extract first 3-digit number from response
        numbers = re.findall(r'\b\d{1,3}\b', answer_extraction)
        if numbers:
            answer = numbers[0].zfill(3)  # Pad with leading zeros if needed
            # Ensure it's exactly 3 digits
            if len(answer) > 3:
                answer = answer[-3:]  # Take last 3 digits if too long
        else:
            answer = "000"  # Default fallback
        
        return answer