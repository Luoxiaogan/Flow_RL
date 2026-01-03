# Workflow ID: mgsmbn_28_0
# Benchmark: mgsmbn
# Data Indices: [61]

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

        # PHASE 1: PARALLEL LINGUISTIC & MATHEMATICAL DECOMPOSITION
        entity_analysis_task = self.generate(
            instruction="""Perform deep entity-action decomposition:
            1. Identify ALL named entities (people, objects, containers)
            2. Map each entity to its initial quantity and unit
            3. Extract ALL actions (gave, received, divided, remaining, etc.)
            4. Establish chronological or logical sequence of actions
            5. Flag any ambiguous pronouns or references
            6. Output in structured markdown format with clear sections""",
            context=""
        )
        
        quantity_analysis_task = self.generate(
            instruction="""Perform deep quantity-operation decomposition:
            1. Extract ALL numerical values and their contextual meaning
            2. Identify mathematical operations implied (add, subtract, multiply, divide, fraction, percentage)
            3. Map operations to entities and actions
            4. Identify dependencies between operations
            5. Flag any unit inconsistencies or missing conversions
            6. Output in structured markdown format with clear sections""",
            context=""
        )

        # Execute parallel decomposition
        entity_analysis, quantity_analysis = await asyncio.gather(
            entity_analysis_task, quantity_analysis_task
        )

        # PHASE 2: ENSEMBLE SYNTHESIS INTO UNIFIED PROBLEM MODEL
        unified_model = await self.ensemble(
            instruction="""Synthesize entity and quantity analyses into a single coherent problem model:
            1. Resolve any conflicts between entity and quantity interpretations
            2. Create a step-by-step mathematical narrative with explicit operations
            3. Include units and constraints for each step
            4. Highlight any remaining ambiguities that require assumption
            5. Format as numbered steps with clear inputs, operations, and outputs
            6. End with a precise statement of what needs to be calculated""",
            contexts_list=[entity_analysis, quantity_analysis]
        )

        # PHASE 3: DYNAMIC ASSUMPTION TESTING (if ambiguity detected)
        ambiguity_check = await self.generate(
            instruction="""Critically evaluate the unified model:
            1. Does it contain any conditional language (if, possibly, alternatively)?
            2. Are there multiple valid interpretations of the sequence?
            3. Are units or constraints still ambiguous?
            4. Return 'AMBIGUOUS' if yes, 'CLEAR' if no, with brief justification""",
            context=unified_model
        )

        if "AMBIGUOUS" in ambiguity_check.upper():
            # Generate multiple assumption-based solutions
            assumption_paths = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate Solution Path A:
                    Assume the most common interpretation for ambiguous elements.
                    {unified_model}
                    Provide complete step-by-step calculation with final answer.""",
                    context=unified_model
                ),
                self.generate(
                    instruction=f"""Generate Solution Path B:
                    Assume the alternative interpretation for ambiguous elements.
                    {unified_model}
                    Provide complete step-by-step calculation with final answer.""",
                    context=unified_model
                )
            )
            
            # Resolve via constraint validation
            unified_model = await self.ensemble(
                instruction="""Select the most plausible solution path:
                1. Evaluate which path respects real-world constraints (no negative quantities, integer people, etc.)
                2. Prefer interpretations that maintain unit consistency
                3. Choose the path most aligned with elementary school level reasoning
                4. Output the selected path with clear justification""",
                contexts_list=assumption_paths
            )

        # PHASE 4: CONSTRAINT-AWARE PROGRAMMING
        constraint_manifest = await self.generate(
            instruction="""Generate a constraint manifest for code execution:
            1. List all units involved and required conversions
            2. Specify domain constraints (non-negative, integer-only, etc.)
            3. Define precision requirements (decimal places, rounding rules)
            4. List forbidden operations or values
            5. Format as bullet points for direct injection into code comments""",
            context=unified_model
        )

        code_solution = await self.programmer(
            instruction=f"""Generate and execute Python code to solve the problem:
            CONSTRAINTS:
            {constraint_manifest}

            STEPS TO FOLLOW:
            1. Define all initial quantities as variables with units in comments
            2. Implement each mathematical step from the unified model
            3. Include assertions for constraints after each operation
            4. Handle unit conversions explicitly
            5. Print only the final numerical answer (no text)
            6. If assertion fails, raise ValueError with specific constraint violation
            
            Example structure:
            # Initial: 24 liters total
            total_water = 24
            # Each girl gets 1/6
            per_girl = total_water * (1/6)
            ...""",
            context=unified_model,
            max_retries=3
        )

        # PHASE 5: REFLECTIVE VALIDATION
        explanation = await self.generate(
            instruction="""Generate a natural language explanation of the solution:
            1. Restate the problem in simple terms
            2. Explain each calculation step in context
            3. Verify that the final answer makes sense in the real-world scenario
            4. Confirm unit consistency throughout
            5. Check that no elementary-level constraints are violated
            6. Format as a clear, paragraph-style explanation""",
            context=f"Solution: {code_solution}\nModel: {unified_model}"
        )

        final_answer = await self.revise(
            instruction="""Extract and verify the final numerical answer:
            1. Locate the numerical answer in the code output
            2. Confirm it matches the explanation's conclusion
            3. Ensure it's a single number (integer or decimal)
            4. Remove any units or text - only the number
            5. If discrepancy found, return 'ERROR' and explain""",
            context=f"Code Output: {code_solution}\nExplanation: {explanation}"
        )

        # Extract pure number using regex as final safeguard
        number_match = re.search(r'(-?\d+\.?\d*)', final_answer)
        if number_match:
            return number_match.group(1)
        else:
            # Fallback: try to extract from code solution directly
            fallback_match = re.search(r'(-?\d+\.?\d*)', code_solution)
            if fallback_match:
                return fallback_match.group(1)
            else:
                return "0"  # Ultimate fallback - should never reach here