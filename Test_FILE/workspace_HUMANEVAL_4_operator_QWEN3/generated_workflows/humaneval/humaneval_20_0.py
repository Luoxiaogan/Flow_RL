# Workflow ID: humaneval_20_0
# Benchmark: humaneval
# Data Indices: [126, 11]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Deep structural analysis - extract signature, constraints, edge cases
        analysis = await self.generate(
            instruction="""Perform deep structural analysis of the problem:
            1. Extract the exact function name and parameter list from the signature.
            2. Parse all examples in the docstring - list input/output pairs.
            3. Identify explicit constraints (e.g., "assume no negative numbers").
            4. Infer implicit constraints by comparing examples (what makes outputs differ?).
            5. Predict likely edge cases not shown (empty input, single element, boundary values).
            6. Classify problem complexity: simple (1-2 examples, no conditionals) vs complex (many examples, conditionals, edge cases).
            7. Note required return type precision (int vs float, string vs list, etc.).
            Format as structured JSON with keys: function_name, parameters, examples, explicit_constraints, implicit_constraints, edge_cases, complexity, return_type.""",
            context=""
        )

        # Step 2: Conditional forking - generate multiple candidates for complex problems
        complexity = "simple"
        if "complex" in analysis.lower() or "many examples" in analysis.lower() or "conditional" in analysis.lower():
            complexity = "complex"

        if complexity == "complex":
            # Generate 3 different solution strategies in parallel
            candidates = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate Solution Candidate 1 (Direct Approach):
                    Based on analysis: {analysis}
                    Implement the most straightforward, literal interpretation of the specification.
                    Focus on clarity and direct mapping from examples to code.
                    Do not optimize or add extra features.
                    Ensure function name matches ENTRY POINT exactly.
                    Return code only - no explanations.""",
                    context=analysis
                ),
                self.generate(
                    instruction=f"""Generate Solution Candidate 2 (Algorithmic Approach):
                    Based on analysis: {analysis}
                    Implement using a more algorithmic or mathematical approach.
                    Consider edge cases and constraints identified in analysis.
                    Use efficient patterns if applicable, but prioritize correctness over performance.
                    Ensure function name matches ENTRY POINT exactly.
                    Return code only - no explanations.""",
                    context=analysis
                ),
                self.generate(
                    instruction=f"""Generate Solution Candidate 3 (Defensive Approach):
                    Based on analysis: {analysis}
                    Implement with explicit handling of all identified edge cases and constraints.
                    Add comments for each constraint being addressed.
                    Ensure function name matches ENTRY POINT exactly.
                    Return code only - no explanations.""",
                    context=analysis
                )
            )
        else:
            # Simple problem - generate single candidate
            single_candidate = await self.generate(
                instruction=f"""Generate Solution:
                Based on analysis: {analysis}
                Implement the simplest possible solution that satisfies all examples and constraints.
                Ensure function name matches ENTRY POINT exactly.
                Return code only - no explanations.""",
                context=analysis
            )
            candidates = [single_candidate]

        # Step 3: Self-test simulation - validate each candidate against examples
        validated_candidates = []
        for i, candidate in enumerate(candidates):
            validation = await self.generate(
                instruction=f"""Simulate Testing:
                Given candidate code:
                {candidate}
                
                And problem analysis:
                {analysis}
                
                Simulate execution against ALL examples in the docstring.
                For each example, verify:
                1. Function name matches ENTRY POINT exactly.
                2. Parameter count and names match signature.
                3. Return type matches expected type (int/float/string/etc).
                4. Output matches expected output for each input.
                5. All explicit and implicit constraints are satisfied.
                6. Edge cases are handled correctly.
                
                If any test fails, explain why.
                If all pass, output "PASSES_ALL_TESTS".
                Be extremely strict - any mismatch is a failure.""",
                context=candidate
            )
            if "PASSES_ALL_TESTS" in validation:
                validated_candidates.append(candidate)
            else:
                # Revise failed candidate
                revised = await self.revise(
                    instruction=f"""Revise Code to Fix Failures:
                    Original code failed validation: {validation}
                    Problem analysis: {analysis}
                    
                    Fix all identified issues while preserving core logic.
                    Ensure:
                    - Function name matches ENTRY POINT exactly
                    - Parameters match signature
                    - Return type precision is correct
                    - All examples pass
                    - No over-engineering (only implement what's specified)
                    
                    Return revised code only - no explanations.""",
                    context=candidate
                )
                # Re-validate revised code
                revalidation = await self.generate(
                    instruction=f"""Re-simulate Testing:
                    Given revised code:
                    {revised}
                    
                    And problem analysis:
                    {analysis}
                    
                    Simulate execution against ALL examples.
                    Output "PASSES_ALL_TESTS" if all pass, otherwise explain failures.""",
                    context=revised
                )
                if "PASSES_ALL_TESTS" in revalidation:
                    validated_candidates.append(revised)
                else:
                    # If still failing, keep original for ensemble (might be false negative)
                    validated_candidates.append(candidate)

        # Step 4: Ensemble selection - choose best candidate
        if len(validated_candidates) > 1:
            final_code = await self.ensemble(
                instruction=f"""Select Best Solution:
                Problem analysis: {analysis}
                
                Candidates:
                {chr(10).join([f'Candidate {i+1}: {c}' for i, c in enumerate(validated_candidates)])}
                
                Select the candidate that:
                1. Passes all simulated tests (if any do)
                2. Best matches specification (examples, constraints, edge cases)
                3. Is most minimal (no extra features or complexity)
                4. Has correct function name and signature
                5. Returns correct type precision
                
                If multiple pass all tests, choose the simplest.
                Return selected code only - no explanations.""",
                contexts_list=validated_candidates
            )
        else:
            final_code = validated_candidates[0] if validated_candidates else candidates[0]

        # Step 5: Final polish - ensure exact compliance
        polished_code = await self.revise(
            instruction=f"""Final Compliance Check:
            Problem analysis: {analysis}
            
            Ensure code:
            1. Function name matches ENTRY POINT exactly (case-sensitive)
            2. No extra imports or modules (unless explicitly required)
            3. No additional parameters or return values
            4. Minimal and focused - only implements what's specified
            5. Return type precision matches examples exactly
            6. Handles all identified edge cases
            
            If any issue found, fix it. Otherwise, return code unchanged.
            Return code only - no explanations.""",
            context=final_code
        )

        return polished_code