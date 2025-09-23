# Workflow ID: mbppplus_2_0
# Benchmark: mbppplus
# Data Indices: [370, 75, 129]

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
        import json

        # Phase 1: Problem Classification
        classification = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Classify along these dimensions:
            1. Problem Type: Algorithmic (DP/greedy), Data Transformation (filter/map), or Library-Assisted (regex/itertools)
            2. Statefulness: Does solution require maintaining state across iterations? (Yes/No)
            3. Order Sensitivity: Is output order critical? (Yes/No)
            4. Edge Case Profile: What edge cases are likely? (empty input, single element, duplicates, type boundaries)
            5. Return Type: What exact data type must be returned? (list/tuple/set/string/int)
            6. Failure Modes: What are common pitfalls for this problem class?
            Output as JSON with keys: type, stateful, order_sensitive, edge_cases, return_type, failure_modes""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate ALGORITHMIC solution strategy for this problem:
                Classification: {classification}
                Focus on: Dynamic programming, greedy approaches, recursion, or mathematical induction.
                Include: 
                - Pseudocode with clear state transitions
                - Time/space complexity analysis
                - Handling of edge cases identified in classification
                - Why this approach is suitable for the problem structure""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate DATA TRANSFORMATION solution strategy for this problem:
                Classification: {classification}
                Focus on: Filtering, mapping, reducing, or set operations.
                Include:
                - Step-by-step data flow diagram in text
                - How order and duplicates are handled
                - Built-in Python functions that could be leveraged
                - Memory efficiency considerations""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate LIBRARY-ASSISTED solution strategy for this problem:
                Classification: {classification}
                Focus on: Using standard library modules (re, itertools, collections, etc.)
                Include:
                - Specific functions/modules to use and why
                - Pattern matching or grouping logic
                - Performance implications
                - Compatibility with edge cases""",
                context=""
            )
        ]
        strategies = await asyncio.gather(*strategy_tasks)

        # Phase 3: Adversarial Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize a robust solution strategy through adversarial critique:
            1. For each candidate strategy, identify its most critical vulnerability (edge case failure, performance bottleneck, logical flaw)
            2. Propose modifications to address these vulnerabilities
            3. Combine the strongest elements into a hybrid approach
            4. Output final strategy as: 
               - Core algorithm/pattern
               - Edge case handling protocol
               - Validation checkpoints
               - Recommended Python constructs
            Prioritize correctness and edge case resilience over elegance.""",
            contexts_list=strategies
        )

        # Phase 4: Code Generation with Validation
        initial_code = await self.generate(
            instruction=f"""Generate Python function implementation with embedded validation:
            Strategy: {synthesized_strategy}
            Requirements:
            - Match EXACT function signature from problem
            - Include type hints if return type specified in classification
            - Add internal validation: after computation, check for edge case compliance and return (result, confidence_0_to_1)
            - Confidence = 1.0 only if all edge cases from classification are explicitly handled
            - Use defensive programming: type checks, length checks, boundary checks
            - Import required modules INSIDE function if needed
            Output ONLY the function code, no explanations.""",
            context=synthesized_strategy
        )

        # Phase 5: Iterative Refinement
        current_code = initial_code
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Simulate test execution and provide revision directives:
                Function code: {current_code}
                Classification: {classification}
                Check:
                1. Does it handle ALL edge cases from classification?
                2. Is return type exactly as specified?
                3. Are there any type conversion errors?
                4. Does confidence score logic cover critical failure modes?
                If any issue found, provide specific revision instructions. If perfect, output 'APPROVED'.""",
                context=current_code
            )
            
            if "APPROVED" in validation_feedback:
                break
                
            current_code = await self.revise(
                instruction=f"""Revise code based on feedback:
                Feedback: {validation_feedback}
                Requirements:
                - Fix ALL identified issues
                - Maintain function signature
                - Improve confidence scoring logic
                - Add missing edge case handlers
                - Preserve existing correct functionality
                Output ONLY the revised function code.""",
                context=current_code
            )

        # Phase 6: Final Sanitization
        final_code = await self.summarize(
            instruction="""Sanitize final code for production:
            1. Remove any debugging scaffolding or confidence scoring
            2. Ensure function signature EXACTLY matches original problem
            3. Optimize imports (move outside function if safe)
            4. Simplify without changing behavior
            5. Verify return type consistency
            Output ONLY the clean function implementation, ready for testing.""",
            context=current_code
        )

        return final_code