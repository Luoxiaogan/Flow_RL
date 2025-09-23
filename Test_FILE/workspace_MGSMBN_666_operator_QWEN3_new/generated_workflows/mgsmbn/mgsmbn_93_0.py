# Workflow ID: mgsmbn_93_0
# Benchmark: mgsmbn
# Data Indices: [155, 2]

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

        # PHASE 1: SEMANTIC DECOMPOSITION - Break problem into state transitions
        decomposition_instruction = """
        Decompose this Bengali word problem into a sequence of state-changing events. 
        Each subproblem should represent a discrete change in quantities or states.
        Format each subproblem as:
        - ID: step_N
        - Description: What changes? (Include entities, actions, and numerical effects)
        - Dependencies: Which previous steps must be completed first?
        
        Focus on:
        1. Identifying initial quantities and entities
        2. Mapping each action to a mathematical operation (add, remove, transform, etc.)
        3. Preserving temporal order and dependencies
        4. Tracking units (টাকা, জিনিস, মিটার, etc.) at each step
        5. Highlighting the final query (what needs to be calculated)
        
        Example: 
        "শুক্রবার 18টি গোলাপি ফ্লেমিংগো রাখা হয়" → Initial state: pink_flamingos = 18
        "এক তৃতীয়াংশ ফিরিয়ে নেওয়া হয়" → Operation: remove 1/3 of current pink → pink_flamingos -= 6
        """
        
        try:
            decomposition = await self.decompose(
                instruction=decomposition_instruction,
                context=""
            )
        except Exception:
            # Fallback: Direct solve if decomposition fails
            direct_solve = await self.programmer(
                instruction="Solve this Bengali math problem directly. Extract numbers and operations from text. Show all steps.",
                context=""
            )
            return direct_solve

        # PHASE 2: PARALLEL HYPOTHESIS GENERATION - Interpret from multiple angles
        hypothesis_instructions = [
            """
            Interpret this problem as a literal mathematical translation. 
            Extract all numbers and map Bengali action verbs to +, -, ×, ÷.
            Ignore context - focus only on explicit numerical operations.
            Output: Step-by-step calculation sequence.
            """,
            """
            Interpret this problem as a real-world simulation. 
            Consider physical constraints: no negative quantities, no fractional people/objects.
            Track units at every step. Adjust operations if they violate real-world plausibility.
            Output: Simulation narrative with unit tracking.
            """,
            """
            Interpret this problem with unit-consistency as the primary constraint.
            Identify all units mentioned. Ensure every operation preserves or converts units correctly.
            Reject any step that creates unit mismatches. Propose unit-aware calculations.
            Output: Unit-consistent calculation path.
            """
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # PHASE 3: SYNTHESIZE INTERPRETATIONS
        synthesis_instruction = """
        You are given three interpretations of the same Bengali math problem:
        1. Literal mathematical translation
        2. Real-world simulation with constraints
        3. Unit-consistency focused approach
        
        Synthesize these into one coherent solution plan that:
        - Preserves mathematical accuracy
        - Respects real-world constraints (no negatives, no fractions of discrete objects)
        - Maintains unit consistency throughout
        - Follows the temporal sequence of events
        - Clearly states the final calculation needed
        
        Format as:
        Steps:
        1. [Action] → [Calculation] (Units: ...)
        2. [Action] → [Calculation] (Units: ...)
        ...
        Final Query: [What to compute]
        """
        
        synthesized_plan = await self.ensemble(
            instruction=synthesis_instruction,
            contexts_list=hypotheses
        )

        # PHASE 4: GENERATE VALIDATED CODE
        code_instruction = f"""
        Given this synthesized solution plan:
        {synthesized_plan}
        
        AND the original decomposition:
        {json.dumps(decomposition, ensure_ascii=False, indent=2)}
        
        Generate Python code that:
        1. Initializes variables with initial quantities and units
        2. Executes each step in sequence with assertions for:
           - Non-negative quantities (for countable objects)
           - Unit consistency (no adding meters to taka)
           - Fractional constraints (if problem implies whole numbers)
        3. Computes the final answer
        4. Prints ONLY the final numerical answer (no explanations)
        
        Include detailed comments mapping each code line to problem steps.
        Use variable names that reflect entities (e.g., pink_flamingos, total_distance).
        """
        
        code_result = await self.programmer(
            instruction=code_instruction,
            context=synthesized_plan
        )

        # PHASE 5: VALIDATE AND REVISE (at most 2 iterations)
        for attempt in range(2):
            validation_instruction = f"""
            Validate this solution against the original Bengali problem:
            Solution: {code_result}
            Original Problem: {self.problem_text}
            
            Check:
            1. Does the final answer make narrative sense?
            2. Are all steps from the problem accounted for?
            3. Are units handled correctly?
            4. Are real-world constraints respected?
            5. Is the answer format correct (single number)?
            
            If valid, output "VALID: [answer]".
            If invalid, output "INVALID: [specific reason]" and suggest correction.
            """
            
            validation = await self.generate(
                instruction=validation_instruction,
                context=code_result
            )
            
            if "VALID:" in validation:
                # Extract final answer
                try:
                    answer = validation.split("VALID:")[1].strip().split()[0]
                    return answer
                except:
                    return code_result  # Fallback to raw output
            else:
                # Revise based on validation feedback
                code_result = await self.revise(
                    instruction=f"""
                    Revise this solution based on validation feedback:
                    {validation}
                    
                    Requirements:
                    - Fix the specific issue identified
                    - Maintain all previous constraints (units, non-negativity, etc.)
                    - Keep code structure but correct logic
                    - Output only the corrected code and final answer
                    """,
                    context=code_result
                )

        # Final fallback
        return code_result