# Workflow ID: mbppplus_43_0
# Benchmark: mbppplus
# Data Indices: [96, 302]

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

        # PHASE 1: Problem Classification & Requirement Extraction
        classification = await self.generate(
            instruction="""Perform deep problem analysis with this structure:
            1. Problem Category: Classify as [List Operations, Bit Manipulation, String Processing, Mathematical, Logical, Other]
            2. Input/Output Specification: Exact types, formats, and constraints
            3. Edge Cases: List ALL possible edge cases (empty, single element, negatives, zeros, duplicates, type boundaries)
            4. Algorithmic Patterns: Identify known patterns or standard approaches
            5. Output Format: Exact return type and structure required
            Be exhaustive. This classification drives all subsequent steps.""",
            context=""
        )

        # PHASE 2: Parallel Solution Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate solution strategy focusing on MATHEMATICAL ELEGANCE:
                Classification Context: {classification}
                - Use mathematical insights and optimizations
                - Minimize loops and conditionals where possible
                - Prioritize computational efficiency
                - Include edge case handling as mathematical boundary conditions""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution strategy focusing on BRUTE-FORCE CLARITY:
                Classification Context: {classification}
                - Use explicit, readable step-by-step logic
                - Prioritize code clarity over performance
                - Include comprehensive conditional checks
                - Document edge case handling explicitly""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution strategy focusing on EDGE-CASE ROBUSTNESS:
                Classification Context: {classification}
                - Systematically handle every edge case identified
                - Use defensive programming patterns
                - Include input validation and type checking
                - Prioritize correctness over elegance""",
                context=""
            )
        ]
        
        strategies = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the three strategies into one optimal approach:
            - Combine mathematical efficiency with brute-force clarity
            - Integrate comprehensive edge-case handling
            - Ensure solution is both performant and readable
            - Maintain exact output format requirements
            - Resolve any contradictions between strategies
            Output only the unified strategy description.""",
            contexts_list=strategies
        )

        # PHASE 4: Validation Loop with Test Case Generation
        final_strategy = synthesized_strategy
        for validation_round in range(3):
            test_cases = await self.programmer(
                instruction=f"""Generate comprehensive test cases based on strategy:
                Strategy: {final_strategy}
                Classification: {classification}
                - Include edge cases identified in classification
                - Generate 5-7 diverse test cases
                - Include boundary values and pathological cases
                - Format as Python assert statements
                Return only the assert statements.""",
                context=""
            )
            
            validation = await self.generate(
                instruction=f"""Validate strategy against generated test cases:
                Strategy: {final_strategy}
                Test Cases: {test_cases}
                - Check for logical gaps or contradictions
                - Identify any edge cases not properly handled
                - Suggest specific improvements if needed
                If no issues found, respond 'VALIDATED'. Otherwise, describe fixes needed.""",
                context=""
            )
            
            if "VALIDATED" in validation.upper():
                break
            else:
                final_strategy = await self.revise(
                    instruction=f"""Revise strategy based on validation feedback:
                    Current Strategy: {final_strategy}
                    Validation Feedback: {validation}
                    Test Cases: {test_cases}
                    - Address all identified gaps
                    - Strengthen edge case handling
                    - Maintain core algorithmic approach
                    Output revised strategy.""",
                    context=final_strategy
                )

        # PHASE 5: Pseudocode Generation & Refinement
        pseudocode = await self.generate(
            instruction=f"""Generate detailed pseudocode from strategy:
            Strategy: {final_strategy}
            Classification: {classification}
            - Include explicit edge case handling blocks
            - Annotate type expectations and return format
            - Use clear, step-by-step logic
            - Mark sections for potential optimization
            Output only pseudocode with no additional text.""",
            context=""
        )

        # PHASE 6: Code Implementation with Strict Formatting
        implementation = await self.revise(
            instruction="""Convert pseudocode to Python implementation with STRICT requirements:
            - Use EXACT function name and signature from problem
            - Include necessary imports inside function if needed
            - Return appropriate data types as specified
            - Handle all edge cases identified in classification
            - Code must be production-ready and pass all test cases
            - Return ONLY the function implementation - no explanations, no markdown
            - Strip all extra text, comments, or formatting
            - Ensure perfect syntax and indentation""",
            context=pseudocode
        )

        # PHASE 7: Shadow Implementation & Consensus
        shadow_implementation = await self.programmer(
            instruction=f"""Generate minimal correct implementation:
            Problem: {self.problem_text}
            Classification: {classification}
            - Focus on core logic only
            - Ignore optimizations
            - Handle only essential edge cases
            - Return ONLY function implementation
            This serves as validation against over-engineering.""",
            context=""
        )

        # Final consensus between main and shadow implementations
        final_code = await self.ensemble(
            instruction="""Select final implementation with these criteria:
            1. Must match exact function signature required
            2. Must handle all edge cases from classification
            3. Prefer implementation that is both correct and concise
            4. If implementations differ in logic (not just style), choose the more defensive/robust version
            5. Ensure output format matches problem requirements exactly
            Return ONLY the selected implementation - no additional text.""",
            contexts_list=[implementation, shadow_implementation]
        )

        # Clean up any residual markdown or formatting
        clean_code = await self.revise(
            instruction="""Final cleanup:
            - Remove any markdown code block indicators
            - Remove any explanatory text before or after code
            - Ensure only pure Python function implementation remains
            - Verify function signature matches problem exactly
            - No imports outside function unless specified
            Return only the cleaned implementation.""",
            context=final_code
        )

        return clean_code