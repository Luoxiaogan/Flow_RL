# Workflow ID: mbppplus_152_0
# Benchmark: mbppplus
# Data Indices: [319, 173]

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

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break this programming problem into essential subproblems:
            1. INPUT SPEC: What is the exact input type and structure? (e.g., list of tuples, string, etc.)
            2. OUTPUT SPEC: What is the required output type and format? (e.g., string representation, boolean, etc.)
            3. TRANSFORMATION RULE: What logic must be applied to transform input to output?
            4. EDGE CASES: What boundary conditions must be handled? (empty inputs, single elements, etc.)
            5. FORMAT CONSTRAINTS: Are there specific formatting requirements for the output?
            Return each as a separate subproblem with clear dependencies.""",
            context=""
        )

        # Step 2: Parallel hypothesis generation for each decomposition component
        hypotheses = await asyncio.gather(
            self.generate(
                instruction="""Analyze the problem description and test cases to infer the precise transformation rule.
                Consider: What conditions trigger inclusion/exclusion? What operations are performed?
                Express the rule in clear, imperative language suitable for code implementation.""",
                context=""
            ),
            self.generate(
                instruction="""Examine the test cases to determine the exact output format required.
                Note: The format may differ from logical expectations (e.g., returning string instead of list).
                Identify any string formatting, type casting, or structural requirements explicitly shown in assertions.""",
                context=""
            ),
            self.generate(
                instruction="""Identify all edge cases that must be handled, even if not explicitly stated.
                Consider: empty inputs, single-element inputs, boundary values, type variations, and special values.
                For each, specify how the solution should behave based on problem context and test cases.""",
                context=""
            )
        )

        # Step 3: Adversarial validation of hypotheses
        validated_hypotheses = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically evaluate this hypothesis for completeness and robustness:
                - Does it handle all edge cases?
                - Is it consistent with all test cases?
                - Are there ambiguous interpretations that need clarification?
                - What could go wrong in implementation?
                Strengthen the hypothesis to address weaknesses.""",
                context=hypothesis
            ) for hypothesis in hypotheses]
        )

        # Step 4: Ensemble synthesis of validated hypotheses
        synthesized_spec = await self.ensemble(
            instruction="""Synthesize the validated hypotheses into a single, coherent specification for code generation.
            Prioritize: 
            1. Correctness on all test cases
            2. Robustness against edge cases
            3. Exact output format matching
            4. Code simplicity and readability
            Return a comprehensive implementation specification that leaves no ambiguity.""",
            contexts_list=validated_hypotheses
        )

        # Step 5: Generate initial code implementation
        code_attempt = await self.programmer(
            instruction=f"""Implement the solution according to this specification:
            {synthesized_spec}
            
            Requirements:
            - Use exact function signature from problem
            - Handle all identified edge cases
            - Return output in precisely the required format
            - Include necessary imports
            - Write clean, readable code with clear variable names""",
            context="",
            max_retries=1
        )

        # Step 6: Iterative refinement based on test case validation
        current_code = code_attempt
        for iteration in range(3):  # Allow up to 3 refinement cycles
            validation_feedback = await self.generate(
                instruction=f"""Analyze this code against the problem's test cases and requirements:
                {current_code}
                
                Identify:
                1. Which test cases would fail and why
                2. Edge cases not properly handled
                3. Format mismatches in output
                4. Logical errors in implementation
                Be specific and provide exact line numbers if possible.""",
                context=current_code
            )
            
            if "no issues" in validation_feedback.lower() or "all test cases pass" in validation_feedback.lower():
                break
                
            # Revise code based on feedback
            current_code = await self.revise(
                instruction=f"""Fix the issues identified in this feedback:
                {validation_feedback}
                
                Requirements:
                - Preserve correct functionality
                - Fix all identified issues
                - Maintain exact output format
                - Keep code clean and readable""",
                context=current_code
            )

        # Step 7: Final format conformance check
        final_code = await self.revise(
            instruction="""Ensure the code meets ALL format requirements:
            - Returns exactly the type and format shown in test cases (string, list, etc.)
            - No extra whitespace or formatting
            - Function signature matches exactly
            - All necessary imports included at top of function
            - No debug prints or extra output
            Make minimal changes needed for perfect format compliance.""",
            context=current_code
        )

        return final_code