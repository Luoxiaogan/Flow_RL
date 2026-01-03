# Workflow ID: mbppplus_101_0
# Benchmark: mbppplus
# Data Indices: [14, 234]

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

        # Step 1: Parallel problem interpretation from multiple angles
        interpretations = await asyncio.gather(
            self.generate(
                instruction="""Analyze this programming problem from a mathematical perspective:
                - Identify all numerical operations involved
                - Determine if formulas or equations are needed
                - Note any potential division, averages, or statistical operations
                - Highlight mathematical edge cases (division by zero, empty sets, etc.)
                Output a structured analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a data structure perspective:
                - Identify input and output data types (list, tuple, set, string, number)
                - Note any transformations, filters, or mappings required
                - Highlight structural edge cases (empty inputs, single elements, nested structures)
                - Describe the expected output format precisely
                Output a structured analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an algorithmic/logical perspective:
                - Identify decision points, conditions, or branching logic
                - Note any loops, iterations, or recursive patterns needed
                - Highlight logical edge cases (boundary conditions, special values)
                - Describe the step-by-step logical flow required
                Output a structured analysis.""",
                context=""
            )
        )

        # Step 2: Ensemble to synthesize the best interpretation
        synthesized_interpretation = await self.ensemble(
            instruction="""Synthesize the three analyses into one coherent problem specification:
            - Combine mathematical, data structure, and logical insights
            - Resolve any contradictions by prioritizing mathematical precision
            - Explicitly list all edge cases that must be handled
            - Specify the exact function signature and return type expected
            - Format as a clear, executable specification for code generation.""",
            contexts_list=interpretations
        )

        # Step 3: Decompose into subproblems for systematic handling
        subproblems = await self.decompose(
            instruction="""Break down the synthesized problem specification into atomic subproblems:
            - Each subproblem should be independently solvable
            - Include dependencies if order matters (e.g., validate input before processing)
            - Prioritize edge case handling as separate subproblems
            - Format each as: {'id': 'sp1', 'description': '...', 'dependencies': ''}
            Focus on creating a roadmap for robust implementation.""",
            context=synthesized_interpretation
        )

        # Step 4: Summarize decomposition into a concise code spec
        code_spec = await self.summarize(
            instruction="""Compress the decomposed subproblems into a single, precise code generation specification:
            - Include all edge cases as explicit requirements
            - Specify exact data types for inputs and outputs
            - Note any mathematical formulas or algorithms to use
            - Add defensive programming requirements (input validation, error handling)
            - Format as a bullet-point list of non-negotiable implementation rules.""",
            context=str(subproblems)
        )

        # Step 5: Revise spec to add rigor and edge case handling
        rigorous_spec = await self.revise(
            instruction=f"""Enhance the code specification with maximum robustness:
            - Add explicit handling for all edge cases mentioned in the original problem's 'Common Pitfalls'
            - Ensure type consistency (e.g., return tuple vs list as required)
            - Add input validation for mathematical operations (e.g., division by zero)
            - Include docstring with examples matching the problem's test cases
            - Format as a complete, copy-paste ready specification for the Programmer operator.
            
            Original spec:
            {code_spec}""",
            context=code_spec
        )

        # Step 6: Generate code with Programmer
        code_result = await self.programmer(
            instruction=f"""Generate a Python function that solves the problem exactly as specified:
            - Follow the specification below precisely
            - Include all edge case handling
            - Match the exact function signature from the problem
            - Return the correct data type (list, tuple, etc.)
            - Include no extra output or print statements
            - Ensure the code is clean, efficient, and readable
            
            Specification:
            {rigorous_spec}""",
            context=rigorous_spec,
            max_retries=3
        )

        # Step 7: Extract just the code block from the result (Programmer returns more than just code)
        # Use regex to find the code block between