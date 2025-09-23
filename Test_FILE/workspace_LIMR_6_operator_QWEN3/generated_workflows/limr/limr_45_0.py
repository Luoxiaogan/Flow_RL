# Workflow ID: limr_45_0
# Benchmark: limr
# Data Indices: [203, 316]

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

        # PHASE 1: Problem Deconstruction & Strategy Mapping
        decomposition = await self.decompose(
            instruction="""Break this mathematical problem into atomic, solvable subproblems.
            For each subproblem:
            - State what needs to be computed or proven
            - Identify required mathematical domain (algebra, number theory, combinatorics, etc.)
            - List explicit and implicit constraints
            - Note dependencies on other subproblems
            Prioritize subproblems that can be solved computationally or have clear algorithmic paths.
            Format each as: ID: [domain] Description (Constraints: [...])""",
            context=""
        )

        # PHASE 2: Parallel Solution Exploration
        solution_attempts = []
        computational_subproblems = []
        
        for sub in decomposition:
            sub_id = sub['id']
            sub_desc = sub['description']
            
            # Classify subproblem type for routing
            classification = await self.generate(
                instruction=f"""Classify this subproblem for solution routing:
                Subproblem: {sub_desc}
                
                Determine:
                1. Is this primarily computational (requires calculation) or conceptual (requires proof/insight)?
                2. What mathematical tools are most applicable? (e.g., modular arithmetic, coordinate geometry, generating functions)
                3. Can this be solved with a closed-form formula or requires iterative/algorithmic approach?
                4. What are the expected output constraints? (integer, range, format)
                
                Respond in JSON-like format: {{"type": "computational|conceptual", "tools": [...], "approach": "formula|algorithmic|proof", "constraints": [...]}}""",
                context=sub_desc
            )
            
            if "computational" in classification.lower() or "formula" in classification.lower() or "algorithmic" in classification.lower():
                computational_subproblems.append((sub_id, sub_desc, classification))
            else:
                # Conceptual subproblems handled via Generate
                attempt = await self.generate(
                    instruction=f"""Solve this conceptual subproblem with rigorous mathematical reasoning:
                    {sub_desc}
                    
                    Requirements:
                    - Use formal mathematical notation where appropriate
                    - Show all logical steps
                    - Reference relevant theorems or identities
                    - Verify against stated constraints
                    - Final answer must be extractable as integer 0-999
                    - If multiple answers possible, enumerate and count
                    - Box final answer as \\boxed{{value}}""",
                    context=sub_desc
                )
                solution_attempts.append(attempt)

        # Solve computational subproblems in parallel
        if computational_subproblems:
            computational_results = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""Solve this computational subproblem:
                    {desc}
                    
                    Classification context: {classification}
                    
                    Requirements:
                    - Write clean, well-commented Python code
                    - Include assert statements for validation
                    - Handle edge cases explicitly
                    - Output must be single integer 0-999
                    - Print intermediate steps for verification
                    - If multiple solutions, return count or specified aggregate
                    - Use exact arithmetic (fractions, integers) not floats""",
                    context=desc
                ) for _, desc, classification in computational_subproblems]
            )
            solution_attempts.extend(computational_results)

        # PHASE 3: Adversarial Validation & Refinement
        refined_solutions = []
        for i, attempt in enumerate(solution_attempts):
            # Generate critique
            critique = await self.generate(
                instruction=f"""Critically analyze this solution attempt:
                {attempt}
                
                Check for:
                1. Mathematical errors (algebraic, logical, computational)
                2. Violations of problem constraints
                3. Unjustified assumptions
                4. Missing edge cases
                5. Answer format violations (not integer 0-999)
                6. Incomplete proofs or skipped steps
                
                If errors found, specify exactly what and where.
                If no errors, state "VERIFIED: Solution appears correct."
                
                Be brutally honest and specific.""",
                context=attempt
            )
            
            if "error" in critique.lower() or "violation" in critique.lower() or "assumption" in critique.lower():
                # Revise based on critique
                revised = await self.revise(
                    instruction=f"""Revise this solution based on the critique:
                    Original: {attempt}
                    Critique: {critique}
                    
                    Requirements:
                    - Fix all identified errors
                    - Add missing justifications
                    - Strengthen weak arguments
                    - Re-verify against all constraints
                    - Maintain final answer as integer 0-999
                    - Box final answer as \\boxed{{value}}""",
                    context=attempt
                )
                refined_solutions.append(revised)
            else:
                refined_solutions.append(attempt)

        # PHASE 4: Ensemble Synthesis & Confidence Scoring
        if len(refined_solutions) > 1:
            final_answer = await self.ensemble(
                instruction="""Synthesize these solution attempts into a single definitive answer:
                - Compare intermediate steps for consistency
                - Prefer solutions with explicit verification steps
                - If conflict, identify root cause and resolve
                - Extract final integer answer (0-999)
                - If multiple valid answers, return count as specified in problem
                - Format final output as: \\boxed{XXX} where XXX is 3-digit integer (pad with leading zeros if needed)
                - Include brief justification for selected answer""",
                contexts_list=refined_solutions
            )
        else:
            final_answer = refined_solutions[0] if refined_solutions else "No solution generated"

        # PHASE 5: Meta-Verification & Answer Extraction
        verified_answer = await self.revise(
            instruction="""Final verification and answer extraction:
            1. Confirm final answer is integer between 0 and 999
            2. If answer is outside range, apply modulo 1000 or take absolute value as appropriate
            3. Ensure answer is boxed as \\boxed{XXX} with exactly 3 digits (pad with leading zeros)
            4. Remove all explanatory text - output ONLY the boxed answer
            5. If no valid answer found, return \\boxed{000}
            
            Example valid outputs: \\boxed{042}, \\boxed{999}, \\boxed{001}""",
            context=final_answer
        )

        # Extract just the boxed answer
        match = re.search(r'\\boxed\{(\d{3})\}', verified_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any 3-digit number
            numbers = re.findall(r'\b\d{1,3}\b', verified_answer)
            for num in numbers:
                if len(num) <= 3:
                    return num.zfill(3)
            return "000"