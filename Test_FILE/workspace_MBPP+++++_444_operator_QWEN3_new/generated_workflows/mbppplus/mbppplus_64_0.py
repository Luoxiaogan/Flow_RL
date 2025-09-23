# Workflow ID: mbppplus_64_0
# Benchmark: mbppplus
# Data Indices: [315, 154, 27]

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

        # Step 1: Extract formal contract and requirements
        contract_analysis = await self.generate(
            instruction="""Perform deep contract analysis of this programming problem:
            1. Identify exact input parameters and their expected types
            2. Identify exact return type and format requirements
            3. Extract all explicit constraints from problem description
            4. Infer implicit constraints from test cases and domain conventions
            5. List all edge cases that must be handled (empty inputs, single elements, duplicates, etc.)
            6. Identify any performance or complexity requirements (even if implied)
            7. Note any potential ambiguities in the specification
            Present as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Parallel multi-perspective analysis
        analysis_tasks = [
            self.generate(
                instruction=f"""Mathematical/Algorithmic Analysis:
                Based on the contract: {contract_analysis}
                
                1. Classify the core algorithmic pattern (search, sort, transform, etc.)
                2. Identify applicable algorithms or data structures
                3. Analyze time/space complexity trade-offs
                4. Suggest optimal approach given typical constraints
                5. Consider mathematical properties that could simplify solution
                Provide detailed reasoning with examples.""",
                context=contract_analysis
            ),
            self.generate(
                instruction=f"""Robustness & Edge Case Analysis:
                Based on the contract: {contract_analysis}
                
                1. Systematically identify all possible edge cases
                2. For each edge case, specify expected behavior
                3. Consider: empty inputs, single elements, duplicates, extreme values, type mismatches
                4. Suggest defensive programming techniques
                5. Identify potential failure modes and how to handle them
                Organize as bullet points with clear categorization.""",
                context=contract_analysis
            ),
            self.generate(
                instruction=f"""Type Safety & Interface Analysis:
                Based on the contract: {contract_analysis}
                
                1. Verify input/output type consistency
                2. Identify any type conversion requirements
                3. Check for potential type-related bugs (list vs tuple, int vs float, etc.)
                4. Ensure return type matches exactly what's expected in tests
                5. Suggest type annotations or validation if appropriate
                Present as clear, concise guidelines.""",
                context=contract_analysis
            )
        ]
        
        # Execute parallel analyses
        math_analysis, robustness_analysis, type_analysis = await asyncio.gather(*analysis_tasks)

        # Step 3: Synthesize analyses into unified understanding
        unified_analysis = await self.ensemble(
            instruction="""Synthesize these three analytical perspectives into a unified problem understanding:
            1. Combine mathematical approach with robustness requirements
            2. Integrate type safety constraints with algorithmic choices
            3. Resolve any conflicts between perspectives
            4. Prioritize requirements based on test cases and domain conventions
            5. Create a comprehensive implementation strategy that satisfies all perspectives
            Output should be a coherent, actionable plan for implementation.""",
            contexts_list=[math_analysis, robustness_analysis, type_analysis]
        )

        # Step 4: Generate multiple solution candidates
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Candidate 1:
                Based on unified analysis: {unified_analysis}
                
                Implement a straightforward, readable solution that prioritizes correctness.
                Handle all identified edge cases explicitly.
                Match exact function signature and return types.
                Include clear comments explaining key decisions.
                Output ONLY the function implementation as specified, with no additional text.""",
                context=unified_analysis
            ),
            self.generate(
                instruction=f"""Generate Solution Candidate 2:
                Based on unified analysis: {unified_analysis}
                
                Implement an optimized solution that prioritizes efficiency while maintaining correctness.
                Consider algorithmic improvements over brute force.
                Still handle all edge cases and match exact signature.
                Include brief comments on optimization rationale.
                Output ONLY the function implementation as specified, with no additional text.""",
                context=unified_analysis
            )
        )

        # Step 5: Validate and refine solutions
        validation_tasks = []
        for i, candidate in enumerate(solution_candidates):
            validation = await self.generate(
                instruction=f"""Critically validate this solution candidate:
                {candidate}
                
                Against unified analysis: {unified_analysis}
                
                1. Does it handle ALL identified edge cases?
                2. Does it match exact input/output types?
                3. Is the logic correct for all test cases?
                4. Are there any potential bugs or oversights?
                5. Does it follow best practices for this domain?
                Provide specific, actionable feedback for improvement.""",
                context=candidate
            )
            validation_tasks.append(validation)
        
        # Revise solutions based on validation
        revised_solutions = []
        for i, (candidate, validation) in enumerate(zip(solution_candidates, validation_tasks)):
            revised = await self.revise(
                instruction=f"""Revise this solution based on validation feedback:
                Validation: {validation}
                
                1. Fix all identified issues
                2. Improve clarity and robustness
                3. Ensure perfect type matching
                4. Add necessary edge case handling
                5. Maintain exact function signature
                Output ONLY the function implementation as specified, with no additional text.""",
                context=candidate
            )
            revised_solutions.append(revised)

        # Step 6: Final ensemble selection
        final_solution = await self.ensemble(
            instruction="""Select the best solution from these candidates:
            Consider:
            1. Correctness across all edge cases
            2. Code clarity and maintainability
            3. Efficiency and performance
            4. Adherence to type requirements
            5. Overall robustness
            
            If one solution is clearly superior, select it.
            If solutions have complementary strengths, synthesize a hybrid.
            Output ONLY the function implementation as specified, with no additional text or explanation.""",
            contexts_list=revised_solutions
        )

        # Step 7: Final cleanup to ensure perfect format
        cleaned_solution = await self.revise(
            instruction="""Final cleanup and verification:
            1. Ensure output contains ONLY the function implementation
            2. Verify exact function name and parameter names match specification
            3. Remove any extraneous text, comments, or explanations
            4. Ensure proper indentation and Python syntax
            5. Confirm return type matches requirements exactly
            Output ONLY the clean function implementation with no additional text.""",
            context=final_solution
        )

        return cleaned_solution