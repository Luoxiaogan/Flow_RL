# Workflow ID: humaneval_75_0
# Benchmark: humaneval
# Data Indices: [71, 40]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: PARALLEL PROBLEM DECOMPOSITION
        # Generate three independent interpretations: mathematical, logical, edge-case focused
        math_analysis, logic_analysis, edge_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze this problem from a mathematical/formulaic perspective:
                - Identify any formulas, equations, or numerical relationships implied by the examples
                - Derive step-by-step how inputs transform to outputs
                - Note any precision, rounding, or type requirements
                - Do NOT write code yet — describe the computational logic in plain English
                - Focus on the core calculation or transformation""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a logical/conditional perspective:
                - Identify all decision points, branches, and validation steps
                - Map out the control flow: what conditions lead to what outputs?
                - Extract explicit and implicit constraints from examples
                - Note any early-return or short-circuit conditions
                - Describe the logical structure without writing code""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from an edge-case and boundary perspective:
                - List all boundary conditions implied by examples (min/max values, empty inputs, etc.)
                - What inputs would break a naive implementation?
                - What return types are non-obvious? (e.g., int vs float, -1 as sentinel)
                - Identify any hidden constraints (e.g., "distinct elements", "valid triangle")
                - Focus on robustness and failure modes""",
                context=""
            )
        )

        # PHASE 2: PARALLEL CODE GENERATION FROM EACH PERSPECTIVE
        math_code, logic_code, edge_code = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code based on this mathematical analysis:
                {math_analysis}
                
                Requirements:
                - Use EXACT function name from ENTRY POINT
                - Match return types precisely (int/float/bool) as shown in examples
                - Include all necessary validations BEFORE computation
                - Round or format output exactly as specified
                - Handle edge cases mentioned in analysis
                - Return code ONLY — no explanations, no imports""",
                context=math_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code based on this logical analysis:
                {logic_analysis}
                
                Requirements:
                - Use EXACT function name from ENTRY POINT
                - Implement all conditional branches and validations
                - Early return when possible for efficiency
                - Match example outputs exactly (type and value)
                - Handle all edge cases from analysis
                - Return code ONLY — no explanations, no imports""",
                context=logic_analysis
            ),
            self.generate(
                instruction=f"""Generate Python code focused on edge-case robustness:
                {edge_analysis}
                
                Requirements:
                - Use EXACT function name from ENTRY POINT
                - Prioritize correctness over elegance — explicit checks for all edge cases
                - Return types must match examples precisely
                - Include defensive programming: validate inputs, handle degenerate cases
                - Return code ONLY — no explanations, no imports""",
                context=edge_analysis
            )
        )

        # PHASE 3: ITERATIVE REVISION (up to 2 rounds)
        candidates = [math_code, logic_code, edge_code]
        revised_candidates = []
        
        for candidate in candidates:
            current_code = candidate
            for revision_round in range(2):  # Max 2 revisions
                critique = await self.generate(
                    instruction=f"""Critique this code against the original problem:
                    - Does it handle ALL example cases from the docstring?
                    - Does it use the correct function name?
                    - Are return types exact matches (int vs float matters)?
                    - Are edge cases properly handled?
                    - Any off-by-one errors or logical flaws?
                    - Is the algorithm correct for the problem domain?
                    
                    If perfect, respond "APPROVED". Otherwise, list specific fixes needed.""",
                    context=current_code
                )
                
                if "APPROVED" in critique.upper():
                    break
                
                current_code = await self.revise(
                    instruction=f"""Revise the code to fix these issues:
                    {critique}
                    
                    Requirements:
                    - Preserve correct parts of the original
                    - Fix only the identified issues
                    - Maintain exact function signature and return types
                    - Return revised code ONLY""",
                    context=current_code
                )
            revised_candidates.append(current_code)

        # PHASE 4: ENSEMBLE SYNTHESIS
        final_code = await self.ensemble(
            instruction="""Synthesize the best elements from all candidates:
            - Identify consensus on core algorithm (e.g., all use Heron's formula or nested loops)
            - Pick the most robust edge-case handling
            - Choose the clearest conditional logic
            - Ensure return types match examples exactly
            - Use the correct function name
            - Optimize for correctness, not brevity
            - Return the final code ONLY — no explanations""",
            contexts_list=revised_candidates
        )

        # PHASE 5: SELF-VALIDATION AND EMERGENCY REVISION
        validation_script = await self.generate(
            instruction=f"""Generate a self-test script that validates the code against docstring examples:
            - Parse all >>> examples from the original docstring
            - Convert them into assert statements
            - Include the function definition and asserts in one block
            - Use exact values and types from examples
            - Return the complete test script ONLY""",
            context=final_code
        )

        validation_result = await self.generate(
            instruction=f"""Execute this validation mentally:
            {validation_script}
            
            Does the code pass all asserts? If yes, respond "VALID". 
            If any fail, explain exactly which example fails and why.""",
            context=validation_script
        )

        if "VALID" not in validation_result.upper():
            final_code = await self.revise(
                instruction=f"""EMERGENCY REVISION: Fix the code to pass all docstring examples.
                Validation failed because: {validation_result}
                
                Requirements:
                - Fix only the failing cases
                - Preserve correct behavior for passing cases
                - Match return types and values exactly
                - Return revised code ONLY""",
                context=final_code
            )

        return final_code