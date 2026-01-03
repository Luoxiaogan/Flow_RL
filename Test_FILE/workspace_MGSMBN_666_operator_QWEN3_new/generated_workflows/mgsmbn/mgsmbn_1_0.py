# Workflow ID: mgsmbn_1_0
# Benchmark: mgsmbn
# Data Indices: [56]

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

        # PHASE 1: PARALLEL PERSPECTIVE GENERATION
        # Generate three independent interpretations: linguistic, mathematical, and constraint-based
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""Perform deep linguistic analysis of the Bengali problem. Extract:
                - All numerical values with their contextual descriptors
                - Verbs indicating mathematical operations (যোগ, বিয়োগ, গুণ, ভাগ, অর্ধেক, দ্বিগুণ, etc.)
                - Comparative phrases (চেয়ে বেশি, কম, সমান)
                - Units of measurement (টাকা, বর্গফুট, ঘণ্টা, জিনিস)
                - Temporal or sequential markers (প্রথমে, তারপর, শেষে)
                Ignore narrative elements like names, places, or descriptive adjectives unless they modify quantities.
                Format as structured JSON with keys: numbers, operations, comparisons, units, sequence.""",
                context=""
            ),
            self.generate(
                instruction="""Model the mathematical structure:
                - Identify the problem type: Sequential, Proportional, Distribution, Rate, or Multi-entity
                - Map relationships between quantities (e.g., 'A is half of B' → A = B/2)
                - Identify knowns, unknowns, and implicit constraints
                - Determine if algebraic, arithmetic, or geometric reasoning is needed
                - Note any hidden steps or intermediate calculations required
                Format as structured JSON with keys: problem_type, relationships, knowns, unknowns, constraints, reasoning_type.""",
                context=""
            ),
            self.generate(
                instruction="""Identify real-world constraints and validation rules:
                - Physical impossibilities (negative quantities, fractional people)
                - Unit consistency requirements
                - Boundary conditions (minimum/maximum values)
                - Plausibility checks (e.g., speed can't exceed light speed)
                - Common sense validations (e.g., ages must be positive integers)
                Format as structured JSON with keys: physical_constraints, unit_rules, boundaries, plausibility_checks.""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE INTO COHERENT PROBLEM REPRESENTATION
        synthesized_understanding = await self.ensemble(
            instruction="""Synthesize the three perspectives into a unified problem representation.
            Resolve conflicts by prioritizing:
            1. Mathematical relationships over linguistic ambiguity
            2. Constraint validation over computational convenience
            3. Explicit problem statements over inferred assumptions
            Output must be a comprehensive JSON structure containing:
            - Complete set of known values with units
            - Mathematical relationships as equations or logical statements
            - Step-by-step solution approach
            - Validation criteria for final answer
            - Final answer format specification""",
            contexts_list=perspectives
        )

        # PHASE 3: DECOMPOSE INTO EXECUTABLE SUBPROBLEMS
        subproblems = await self.decompose(
            instruction="""Break down the synthesized problem representation into atomic, executable subproblems.
            Each subproblem must:
            - Be solvable independently given its dependencies
            - Specify required inputs and expected outputs
            - Include validation criteria
            - Reference specific equations or relationships from the synthesized understanding
            - Be ordered by dependency (earlier subproblems must resolve before later ones)
            Format as list of dictionaries with keys: id, description, dependencies, inputs, outputs, validation.""",
            context=synthesized_understanding
        )

        # PHASE 4: SEQUENTIAL EXECUTION WITH VALIDATION
        results = {}
        for subproblem in subproblems:
            sub_id = subproblem['id']
            dependencies = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            
            # Wait for dependencies
            dep_context = "\n".join([f"Result for {dep}: {results.get(dep, 'Not computed yet')}" for dep in dependencies if dep.strip()])
            
            # Execute subproblem
            code_result = await self.programmer(
                instruction=f"""Solve this subproblem using Python:
                Description: {subproblem['description']}
                Dependencies: {dep_context}
                Validation criteria: {subproblem.get('validation', 'None specified')}
                Requirements:
                - Use exact arithmetic (no floating point unless necessary)
                - Handle units appropriately
                - Validate against constraints before returning
                - If validation fails, raise an exception with detailed reason
                - Return only the numerical result, no explanations""",
                context=synthesized_understanding
            )
            
            # Extract numerical result (handle various output formats)
            result_str = await self.summarize(
                instruction="Extract only the numerical result from the code output. If multiple numbers, select the final answer. Remove all text, units, and formatting.",
                context=code_result
            )
            
            # Validate result plausibility
            validation = await self.generate(
                instruction=f"""Validate this result: {result_str}
                Against constraints: {subproblem.get('validation', 'None')}
                Check for:
                - Physical plausibility (no negatives where impossible)
                - Unit consistency
                - Mathematical correctness
                - Boundary compliance
                If valid, return 'VALID: <result>'. If invalid, return 'INVALID: <reason>'""",
                context=synthesized_understanding
            )
            
            if "INVALID" in validation:
                # Attempt revision once
                revised_result = await self.revise(
                    instruction=f"""Fix the invalid result based on validation feedback:
                    Original result: {result_str}
                    Validation feedback: {validation}
                    Constraints: {subproblem.get('validation', 'None')}
                    Return only the corrected numerical value.""",
                    context=code_result
                )
                result_str = await self.summarize(
                    instruction="Extract only the numerical result from the revised output.",
                    context=revised_result
                )
            
            results[sub_id] = result_str.strip()

        # PHASE 5: FINAL ANSWER EXTRACTION AND VERIFICATION
        final_answer_candidates = list(results.values())
        final_answer = await self.ensemble(
            instruction="""Select the final answer from candidates:
            - The last computed subproblem result is primary candidate
            - Verify it answers the original question
            - Cross-check against all validation criteria
            - Ensure it's a single numerical value as required
            - If multiple candidates, select the one that best satisfies all constraints
            Return ONLY the numerical value, nothing else.""",
            contexts_list=[str(x) for x in final_answer_candidates]
        )

        # FINAL SANITY CHECK
        sanity_check = await self.generate(
            instruction=f"""Perform final sanity check on answer: {final_answer}
            Verify:
            - Matches problem requirements
            - No units or text attached
            - Numerically plausible given context
            - Single value as required
            If valid, return the number unchanged. If invalid, return 'ERROR'""",
            context=synthesized_understanding
        )

        if "ERROR" in sanity_check:
            # Fallback: recompute using direct approach
            direct_solution = await self.programmer(
                instruction="""Solve the original problem directly with Python.
                Requirements:
                - Read problem carefully
                - Implement step-by-step solution
                - Validate each step
                - Return only final numerical answer
                - Handle edge cases appropriately""",
                context=""
            )
            final_answer = await self.summarize(
                instruction="Extract only the numerical result. Remove all text, units, and explanations.",
                context=direct_solution
            )

        return final_answer.strip()