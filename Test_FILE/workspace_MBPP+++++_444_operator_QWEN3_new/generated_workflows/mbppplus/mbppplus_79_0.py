# Workflow ID: mbppplus_79_0
# Benchmark: mbppplus
# Data Indices: [92, 97, 87]

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
        import math
        import cmath
        import json

        # Phase 1: Parallel Problem Decomposition
        data_structure_analysis = self.generate(
            instruction="""Analyze the data structures involved in this problem. 
            Identify whether the primary input/output involves strings, dictionaries, tuples, lists, numbers, or complex types.
            Note any constraints on mutability, ordering, or type preservation.
            Extract the exact function signature and parameter names.
            Consider edge cases: empty inputs, single elements, duplicates, type boundaries.
            Format your response as a structured JSON with keys: "input_type", "output_type", "edge_cases", "signature_details".""",
            context=""
        )
        
        computational_intent_analysis = self.generate(
            instruction="""Determine the core computational intent of this function.
            Is it: transforming data (e.g., string cleaning), calculating values (e.g., mathematical operations), 
            reordering/structuring (e.g., sorting), filtering, or validating?
            Identify the precise operation: e.g., 'replace multiple spaces with single space', 
            'sort dictionary by product of tuple keys', 'compute magnitude of complex number'.
            What algorithmic patterns apply? (e.g., regex, sorting with key function, mathematical formula)
            Format as JSON with keys: "operation_type", "algorithmic_approach", "key_formula_or_rule".""",
            context=""
        )
        
        edge_case_sensitivity_analysis = self.generate(
            instruction="""Systematically identify all edge cases and boundary conditions.
            Consider: empty inputs, null/None values, single-element cases, maximum/minimum values, 
            duplicate elements, type mismatches, whitespace variations, precision requirements.
            For each edge case, specify how the function should behave (e.g., 'return empty dict', 'preserve leading/trailing spaces').
            Format as JSON list of objects with keys: "edge_case_description", "expected_behavior".""",
            context=""
        )

        # Await all parallel analyses
        ds_analysis, ci_analysis, ec_analysis = await asyncio.gather(
            data_structure_analysis, computational_intent_analysis, edge_case_sensitivity_analysis
        )

        # Phase 2: Ensemble Synthesis of Problem Signature
        problem_signature = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified, executable problem specification.
            Combine data structure constraints, computational intent, and edge case requirements.
            Produce a detailed implementation blueprint that includes:
            - Exact function signature (name and parameters)
            - Required imports
            - Core algorithm steps
            - Edge case handling logic
            - Expected return type and format
            Format as a structured JSON with keys: "function_name", "parameters", "imports", "algorithm_steps", "edge_case_handlers", "return_type".""",
            contexts_list=[ds_analysis, ci_analysis, ec_analysis]
        )

        # Phase 3: Dual Strategy Implementation Generation
        reference_strategy = await self.generate(
            instruction=f"""Generate a direct implementation mirroring the reference solution approach.
            Use the problem signature: {problem_signature}
            Prioritize clarity and direct translation of the described algorithm.
            Include all necessary imports and handle all specified edge cases.
            Return ONLY the function implementation as a raw code block with no additional text.""",
            context=problem_signature
        )

        alternative_strategy = await self.generate(
            instruction=f"""Generate an alternative implementation using a different but logically equivalent approach.
            For example: if reference uses regex, use iterative string building; if reference uses sorted(), use manual sorting.
            Problem signature: {problem_signature}
            The alternative must handle all edge cases identically to the reference approach.
            Return ONLY the function implementation as a raw code block with no additional text.""",
            context=problem_signature
        )

        # Phase 4: Cross-Validation and Refinement Loop
        implementations = [reference_strategy, alternative_strategy]
        validated_implementations = []
        
        for i in range(2):  # Allow up to 2 refinement cycles
            validation_tasks = []
            for impl in implementations:
                validation = self.generate(
                    instruction=f"""Validate this implementation against the problem signature and edge cases.
                    Problem signature: {problem_signature}
                    Implementation: {impl}
                    Check: correct function name, parameter names, return type, edge case handling, algorithmic correctness.
                    If any issues found, describe them precisely. If perfect, respond "VALID".
                    Otherwise, list all discrepancies in bullet points.""",
                    context=impl
                )
                validation_tasks.append(validation)
            
            validations = await asyncio.gather(*validation_tasks)
            
            # Check if both are valid or if we need refinement
            if all("VALID" in v for v in validations):
                validated_implementations = implementations
                break
            else:
                # Revise implementations based on validation feedback
                revised_implementations = []
                for j, (impl, val) in enumerate(zip(implementations, validations)):
                    if "VALID" in val:
                        revised_implementations.append(impl)
                    else:
                        revised = await self.revise(
                            instruction=f"""Fix all issues identified in validation: {val}
                            Maintain exact function signature and handle all edge cases.
                            Problem signature: {problem_signature}
                            Return ONLY the corrected function implementation as raw code.""",
                            context=impl
                        )
                        revised_implementations.append(revised)
                implementations = revised_implementations
        else:
            # If we exhausted refinements, use ensemble to pick best
            validated_implementations = await self.ensemble(
                instruction="""Select the most correct implementation from the candidates.
                Prioritize: correct function signature, edge case handling, algorithmic accuracy.
                Return ONLY the selected function implementation as raw code.""",
                contexts_list=implementations
            )
            validated_implementations = [validated_implementations]  # Make it a list for consistency

        # Phase 5: Final Output Synthesis and Type Contract Validation
        final_implementation = await self.summarize(
            instruction="""Distill the implementation to its most concise, readable, and correct form.
            Remove any debugging code, redundant comments, or unnecessary complexity.
            Ensure exact function signature is preserved.
            Include only necessary imports.
            Return ONLY the function implementation as raw code with no additional text.""",
            context=validated_implementations[0] if isinstance(validated_implementations, list) else validated_implementations
        )

        # Final contract validation
        contract_check = await self.generate(
            instruction=f"""Verify this implementation meets all contractual requirements:
            - Exact function name and parameter names
            - Correct return type
            - All necessary imports included
            - No extra wrapper functions or classes
            If perfect, return "CONTRACT_MET". Otherwise, list discrepancies.
            Implementation: {final_implementation}""",
            context=final_implementation
        )

        if "CONTRACT_MET" not in contract_check:
            final_implementation = await self.revise(
                instruction=f"""Fix contract violations: {contract_check}
                Preserve all functionality and edge case handling.
                Return ONLY the corrected function implementation as raw code.""",
                context=final_implementation
            )

        return final_implementation