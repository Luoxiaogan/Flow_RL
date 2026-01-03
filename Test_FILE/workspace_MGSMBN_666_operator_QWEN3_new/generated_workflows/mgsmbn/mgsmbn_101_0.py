# Workflow ID: mgsmbn_101_0
# Benchmark: mgsmbn
# Data Indices: [167, 50]

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

        # PHASE 1: MULTI-PERSPECTIVE PROBLEM INTERPRETATION (DIAMOND PATTERN)
        interpretation_instructions = [
            """Analyze this Bengali math problem from a PURELY MATHEMATICAL perspective:
            - Identify all numerical values and their symbolic representations
            - Extract mathematical relationships (equations, inequalities, proportions)
            - Define unknowns and what needs to be solved for
            - Ignore linguistic nuances; focus only on quantitative structure
            - Present as structured mathematical model with variables""",
            
            """Analyze this Bengali math problem from a LINGUISTIC perspective:
            - Identify key Bengali quantifiers (প্রতিটি, আধ, কুড়ি, থেকে কম, দ্বিগুণ etc.)
            - Resolve ambiguous phrases and comparative structures
            - Map Bengali terms to mathematical operations
            - Highlight potential translation pitfalls or double meanings
            - Present as annotated linguistic breakdown""",
            
            """Analyze this Bengali math problem from a CONTEXTUAL/REAL-WORLD perspective:
            - Identify real-world constraints (non-negative quantities, integer counts, unit consistency)
            - Flag physically impossible scenarios
            - Consider practical implications of operations
            - Identify implicit assumptions
            - Present as contextual constraint list"""
        ]

        # Generate parallel interpretations
        interpretations = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in interpretation_instructions]
        )

        # Synthesize into unified problem representation
        unified_representation = await self.ensemble(
            instruction="""Synthesize these three perspectives into a single, coherent problem representation:
            - Combine mathematical structure with linguistic disambiguation
            - Incorporate real-world constraints
            - Resolve any conflicts between perspectives
            - Create a definitive problem specification that can be computationally solved
            - Format: Clear variable definitions, equations, constraints, and target""",
            contexts_list=interpretations
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION
        subproblems = await self.decompose(
            instruction="""Break down this problem into minimal computational subproblems:
            - Each subproblem should be solvable independently if dependencies are met
            - Identify prerequisite relationships between subproblems
            - Assign clear variable names and expected outputs
            - Include unit tracking for each subproblem
            - Return as structured list with dependencies""",
            context=unified_representation
        )

        # PHASE 3: CASCADE WITH FEEDBACK LOOP
        solution = None
        validation_feedback = ""
        
        for attempt in range(3):  # Max 3 refinement cycles
            try:
                # Generate solution code based on current understanding
                solution_attempt = await self.programmer(
                    instruction=f"""Generate Python code to solve this problem based on:
                    Problem Representation: {unified_representation}
                    Subproblems: {subproblems}
                    
                    Requirements:
                    - Solve subproblems in dependency order
                    - Track units throughout calculations
                    - Include intermediate result comments
                    - Final answer must be a single numerical value
                    - Handle edge cases (negative numbers, division by zero)
                    - Return only the final numerical answer""",
                    context=validation_feedback if validation_feedback else unified_representation,
                    max_retries=1
                )

                # Validate solution
                validation = await self.revise(
                    instruction=f"""Critically validate this solution:
                    - Check unit consistency throughout
                    - Verify arithmetic correctness
                    - Ensure answer matches problem constraints
                    - Confirm no logical contradictions
                    - If valid, return 'VALID: <answer>'
                    - If invalid, return 'INVALID: <specific error description>'""",
                    context=solution_attempt
                )

                if "VALID:" in validation:
                    solution = validation.split("VALID:")[1].strip()
                    break
                else:
                    validation_feedback = f"Previous attempt failed: {validation}. Revise approach."
                    
            except Exception as e:
                validation_feedback = f"Execution error: {str(e)}. Try different approach."

        # PHASE 4: FINAL VERIFICATION AND OUTPUT
        if solution is None:
            # Fallback: Simpler direct calculation if cascade failed
            solution = await self.programmer(
                instruction="""Generate simplest possible Python code to solve problem:
                - Ignore complex decomposition
                - Use direct arithmetic operations
                - Return only numerical answer
                - Assume standard interpretations of Bengali terms""",
                context="",
                max_retries=1
            )

        # Extract numerical answer (remove any text, units, or formatting)
        final_answer = re.search(r'[-+]?\d*\.?\d+', str(solution))
        if final_answer:
            return final_answer.group(0)
        else:
            # Last resort: return raw solution
            return str(solution).strip()