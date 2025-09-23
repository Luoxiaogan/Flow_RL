# Workflow ID: limr_27_0
# Benchmark: limr
# Data Indices: [170, 45]

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
        import re
        
        # PHASE 1: STRATEGIC DECOMPOSITION
        decomposition_instruction = """
        Systematically decompose this mathematical problem into minimal necessary subproblems.
        For each subproblem, specify:
        1. Mathematical domain (algebra, combinatorics, number theory, geometry, etc.)
        2. Key technique or theorem required (e.g., modular arithmetic, generating functions, coordinate geometry)
        3. Input-output contract (what inputs it needs, what it produces)
        4. Dependencies (which other subproblems must be solved first)
        5. Potential symmetries or invariants that can be exploited
        Prioritize subproblems that unlock multiple solution paths. Return structured list.
        """
        
        try:
            subproblems = await self.decompose(
                instruction=decomposition_instruction,
                context=""
            )
        except Exception:
            # Fallback: brute force classification if decomposition fails
            classification = await self.generate(
                instruction="Ignore structure. List all possible mathematical domains this could belong to, then pick the most probable with justification.",
                context=""
            )
            subproblems = await self.decompose(
                instruction=f"Given domain classification: {classification}\n" + decomposition_instruction,
                context=""
            )

        # PHASE 2: PARALLEL SOLUTION PATHWAY EXPLORATION
        solution_attempts = []
        
        for i, sp in enumerate(subproblems[:3]):  # Limit to top 3 subproblems to avoid explosion
            sp_id = sp.get('id', f'sp_{i}')
            sp_desc = sp.get('description', '')
            
            # Generate solution attempt for this subproblem from multiple angles
            angle_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""
                    Solve subproblem {sp_id}: {sp_desc}
                    Approach 1: Algebraic/Analytical
                    - Use symbolic manipulation
                    - Apply relevant theorems
                    - Show all steps
                    - Verify intermediate results
                    """,
                    context=""
                ),
                self.generate(
                    instruction=f"""
                    Solve subproblem {sp_id}: {sp_desc}
                    Approach 2: Computational/Algorithmic
                    - Consider brute force or smart enumeration
                    - Look for patterns or recurrences
                    - Use modular arithmetic if applicable
                    - Optimize for integer constraints
                    """,
                    context=""
                ),
                self.generate(
                    instruction=f"""
                    Solve subproblem {sp_id}: {sp_desc}
                    Approach 3: Geometric/Visual
                    - Represent problem spatially if possible
                    - Use symmetry, invariants, or transformations
                    - Apply coordinate geometry or vector methods
                    - Leverage trigonometric identities
                    """,
                    context=""
                )
            )
            
            # Revise each attempt for rigor
            revised_attempts = await asyncio.gather(
                *[self.revise(
                    instruction=f"""
                    Critically revise this solution attempt for subproblem {sp_id}:
                    - Verify all mathematical steps
                    - Check for integer constraint compliance
                    - Ensure no logical gaps or unproven assumptions
                    - Confirm answer format (integer 000-999)
                    - Improve clarity and precision
                    """,
                    context=attempt
                ) for attempt in angle_attempts]
            )
            
            solution_attempts.extend(revised_attempts)

        # PHASE 3: CROSS-VERIFICATION AND ERROR CORRECTION
        verified_solutions = []
        
        for attempt in solution_attempts:
            verification = await self.generate(
                instruction=f"""
                Perform rigorous verification of this solution:
                - Check all calculations step by step
                - Validate against original problem constraints
                - Ensure final answer is integer between 000-999
                - Identify any logical flaws or gaps
                - If valid, output "VERIFIED: <answer>"; if invalid, output "INVALID: <reason>"
                """,
                context=attempt
            )
            
            if "VERIFIED:" in verification:
                verified_solutions.append(attempt)
            else:
                # Attempt repair
                repaired = await self.revise(
                    instruction=f"""
                    Repair this solution based on verification feedback: {verification}
                    - Fix all identified errors
                    - Strengthen weak arguments
                    - Add missing steps
                    - Ensure mathematical rigor
                    - Final answer must be integer 000-999
                    """,
                    context=attempt
                )
                
                # Re-verify
                re_verification = await self.generate(
                    instruction="Re-verify this repaired solution. Output 'VERIFIED: <answer>' or 'INVALID: <reason>'",
                    context=repaired
                )
                
                if "VERIFIED:" in re_verification:
                    verified_solutions.append(repaired)

        # PHASE 4: FINAL SYNTHESIS AND ANSWER EXTRACTION
        if len(verified_solutions) == 0:
            # Emergency fallback: brute force with programmer
            final_answer = await self.programmer(
                instruction="""
                Solve the original problem computationally:
                - Implement algorithm to find exact integer answer
                - Handle all edge cases
                - Return only the integer result (000-999)
                - No explanations, just the number
                """,
                context="",
                max_retries=3
            )
        elif len(verified_solutions) == 1:
            final_answer = verified_solutions[0]
        else:
            # Ensemble synthesis
            final_answer = await self.ensemble(
                instruction="""
                Synthesize these verified solutions into one final answer:
                - Compare all solutions
                - If they agree, output the common answer
                - If they disagree, identify point of divergence and resolve using most mathematically rigorous approach
                - Extract final integer answer (000-999)
                - Format as three-digit number with leading zeros if needed
                """,
                contexts_list=verified_solutions
            )

        # FINAL EXTRACTION AND FORMATTING
        formatted_answer = await self.revise(
            instruction="""
            Extract the final numerical answer from this solution.
            - Must be an integer between 000 and 999
            - If answer is a formula, evaluate it
            - If multiple answers, pick the one that satisfies all constraints
            - Format as three-digit string with leading zeros (e.g., '042')
            - Return ONLY the three-digit string, nothing else
            """,
            context=final_answer
        )
        
        # Ensure it's clean three-digit format
        match = re.search(r'\b(\d{1,3})\b', formatted_answer)
        if match:
            answer = match.group(1).zfill(3)
            if len(answer) == 3 and answer.isdigit():
                return answer
        
        # Ultimate fallback: extract any number and force format
        numbers = re.findall(r'\d+', formatted_answer)
        if numbers:
            return numbers[0].zfill(3)[:3]
        
        # If all else fails, return 000 as placeholder (should never happen)
        return "000"