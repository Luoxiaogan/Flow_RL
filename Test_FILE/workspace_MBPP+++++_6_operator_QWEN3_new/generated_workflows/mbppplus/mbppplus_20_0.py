# Workflow ID: mbppplus_20_0
# Benchmark: mbppplus
# Data Indices: [239, 240]

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

        # Phase 1: Problem Triage & Complexity Analysis
        triage_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem:
            1. Classify problem type: Is it mathematical, algorithmic, data transformation, or logical validation?
            2. Estimate complexity: Is it O(1), O(n), O(n^2), or requires advanced algorithms?
            3. Identify edge cases: What are the likely boundary conditions? (empty inputs, single elements, duplicates, zeros, negatives)
            4. Determine solution approach: Should we use direct implementation, decomposition, or mathematical derivation?
            5. Predict return type requirements: Must we return specific types (list/tuple/set/int/str)?
            6. Assess risk: How likely is it that basic test cases hide complex edge cases?
            Provide a structured JSON-like analysis with clear sections.""",
            context=""
        )

        # Phase 2: Adaptive Strategy Selection
        if "trivial" in triage_analysis.lower() or "simple" in triage_analysis.lower() or "o(1)" in triage_analysis.lower():
            # Direct solution path for simple problems
            initial_code = await self.programmer(
                instruction=f"""Generate a Python function that solves the problem exactly as specified.
                Key constraints from analysis: {triage_analysis}
                - Handle all edge cases mentioned in analysis
                - Return exact type specified in function signature
                - Prioritize correctness over performance for trivial cases
                - Include no extra output or print statements""",
                context=triage_analysis
            )
        else:
            # Complex problem path: Decompose and solve subproblems
            try:
                subproblems = await self.decompose(
                    instruction="""Break this problem into minimal, independent subproblems.
                    Each subproblem should be solvable in isolation.
                    Prioritize logical separation over granularity.
                    Return list of subproblems with clear descriptions and dependencies.""",
                    context=triage_analysis
                )
                
                # Solve subproblems in parallel
                subproblem_solutions = []
                for subproblem in subproblems:
                    subproblem_desc = subproblem.get('description', '')
                    solution = await self.programmer(
                        instruction=f"""Solve this subproblem as part of larger solution:
                        Subproblem: {subproblem_desc}
                        Context: {triage_analysis}
                        - Return only the code snippet or value needed for this subproblem
                        - Handle edge cases specific to this subproblem
                        - Ensure type consistency with overall problem requirements""",
                        context=subproblem_desc
                    )
                    subproblem_solutions.append(solution)
                
                # Ensemble subproblem solutions into final code
                initial_code = await self.ensemble(
                    instruction="""Synthesize these subproblem solutions into a complete, cohesive solution.
                    Ensure:
                    1. Logical flow between subproblems
                    2. Consistent variable naming and scope
                    3. Proper handling of dependencies between subproblems
                    4. Edge case coverage across entire solution
                    5. Exact return type as specified in original problem
                    Return only the complete function implementation.""",
                    contexts_list=subproblem_solutions
                )
            except Exception:
                # Fallback: Direct solution if decomposition fails
                initial_code = await self.programmer(
                    instruction=f"""Generate complete solution (decomposition failed):
                    Problem analysis: {triage_analysis}
                    - Implement robust solution handling all edge cases
                    - Ensure type-correct return value
                    - Prioritize correctness and completeness""",
                    context=triage_analysis
                )

        # Phase 3: Validation & Edge Case Simulation
        validated_code = await self.revise(
            instruction=f"""Critically review this code for edge case failures and type mismatches:
            Original analysis: {triage_analysis}
            
            Perform mental simulation of these edge cases:
            - Empty inputs (empty list, string, etc.)
            - Single element inputs
            - All duplicate values
            - Boundary values (0, -1, max/min values)
            - Type mismatches (list vs tuple vs set)
            - Performance edge cases (very large inputs if applicable)
            
            If any issues found:
            1. Describe the failure scenario
            2. Modify code to handle it
            3. Preserve original function signature and return type
            
            Return only the corrected, robust implementation.""",
            context=initial_code
        )

        # Phase 4: Type & Signature Enforcement
        final_code = await self.revise(
            instruction="""Ensure absolute compliance with function signature and return type:
            - Verify parameter names match exactly
            - Confirm return type (int, str, list, tuple, set) matches problem specification
            - Remove any debug prints or extra outputs
            - Ensure no external dependencies or imports beyond standard library
            - Code must be self-contained function only
            
            If any deviations found, correct them without changing logic.
            Return only the final, submission-ready function implementation.""",
            context=validated_code
        )

        # Phase 5: Confidence Check & Escalation (if needed)
        confidence_check = await self.generate(
            instruction="""Rate confidence in this solution on scale 1-10:
            10 = handles all edge cases, perfect type compliance, logically sound
            1 = likely to fail hidden test cases
            
            If confidence < 8, explain why and what edge cases remain risky.
            If confidence >= 8, just return "CONFIDENT".""",
            context=final_code
        )

        if "confident" not in confidence_check.lower():
            # Low confidence: Generate alternatives and ensemble
            alternative_solutions = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate ALTERNATIVE solution approach 1:
                    Problem analysis: {triage_analysis}
                    Focus: Simplicity and readability
                    Handle all edge cases from analysis""",
                    context=triage_analysis
                ),
                self.programmer(
                    instruction=f"""Generate ALTERNATIVE solution approach 2:
                    Problem analysis: {triage_analysis}
                    Focus: Performance optimization
                    Handle all edge cases from analysis""",
                    context=triage_analysis
                ),
                self.programmer(
                    instruction=f"""Generate ALTERNATIVE solution approach 3:
                    Problem analysis: {triage_analysis}
                    Focus: Mathematical elegance
                    Handle all edge cases from analysis""",
                    context=triage_analysis
                )
            )
            
            # Include original solution in ensemble
            all_solutions = [final_code] + list(alternative_solutions)
            
            final_code = await self.ensemble(
                instruction=f"""Select BEST solution from these candidates:
                Selection criteria:
                1. Correctness across all edge cases
                2. Type compliance with signature
                3. Code clarity and maintainability
                4. Efficiency where applicable
                5. Robustness to hidden test cases
                
                Justify selection briefly, then return ONLY the selected implementation.
                Original analysis: {triage_analysis}""",
                contexts_list=all_solutions
            )

        return final_code