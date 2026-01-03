# Workflow ID: mbppplus_71_0
# Benchmark: mbppplus
# Data Indices: [158, 218]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        import json

        # Step 1: Parallel specification extraction from multiple analytical perspectives
        spec_prompts = [
            """Analyze the problem from a REGULAR EXPRESSION perspective:
            - Identify patterns that can be matched with regex
            - Specify allowed/disallowed characters
            - Define positional constraints (start/end anchors)
            - Extract implicit format rules (e.g., decimal places, digit groups)
            - List edge cases that regex must handle (empty, null, special chars)""",
            
            """Analyze the problem from a STRING PARSING perspective:
            - Break down input into logical components
            - Identify validation steps (type checks, format checks)
            - Specify error conditions and handling
            - Define state transitions for iterative parsing
            - List edge cases for string operations (empty, whitespace, encoding)""",
            
            """Analyze the problem from a DATA STRUCTURE perspective:
            - Identify required data structures (lists, sets, dicts)
            - Specify iteration patterns (sequential, nested, stateful)
            - Define element tracking requirements (counts, positions, transitions)
            - List edge cases for data structures (empty, single, duplicates)
            - Note performance constraints (time/space complexity)"""
        ]

        specifications = await asyncio.gather(
            *[self.generate(instruction=prompt, context="") for prompt in spec_prompts]
        )

        # Step 2: Synthesize specifications into unified contract
        specification_contract = await self.ensemble(
            instruction="""Synthesize these analytical perspectives into a single, comprehensive specification contract:
            - Combine all identified edge cases
            - Resolve conflicting interpretations by choosing most restrictive/robust option
            - Structure as bullet-pointed requirements with priorities
            - Include explicit type signatures and return format
            - Add defensive programming requirements (input validation, error handling)
            - Format as JSON with keys: function_signature, input_constraints, output_format, edge_cases, validation_rules""",
            contexts_list=specifications
        )

        # Step 3: Problem decomposition for complex logic problems
        decomposition = await self.decompose(
            instruction="""Break down the problem into minimal executable subproblems:
            - Each subproblem should be solvable with 1-3 lines of code
            - Specify dependencies between subproblems
            - Include setup, iteration, state tracking, and cleanup phases
            - For each subproblem, note required inputs and expected outputs
            - Prioritize subproblems that handle edge cases first""",
            context=specification_contract
        )

        # Step 4: Generate multiple code candidates using different strategies
        code_strategies = [
            """Implement using REGULAR EXPRESSIONS:
            - Use re.compile for performance
            - Include start/end anchors
            - Handle all edge cases from specification
            - Return boolean or specified type
            - Include input validation and type checking""",
            
            """Implement using STRING METHODS and MANUAL PARSING:
            - Avoid regex, use split, find, slice operations
            - Include explicit state tracking
            - Handle edge cases with conditional checks
            - Return specified type with proper formatting
            - Include defensive checks for None/empty inputs""",
            
            """Implement using DATA STRUCTURE OPERATIONS:
            - Use lists, sets, dicts for tracking
            - Include iteration with index/element tracking
            - Handle transitions and state changes explicitly
            - Return required data structure with correct type
            - Include length checks and boundary conditions"""
        ]

        code_candidates = await asyncio.gather(
            *[self.programmer(
                instruction=f"""{strategy}

                SPECIFICATION CONTRACT:
                {specification_contract}

                DECOMPOSITION PLAN:
                {json.dumps(decomposition, indent=2) if decomposition else 'N/A'}

                REQUIREMENTS:
                - Match exact function signature
                - Handle all edge cases from specification
                - Include type hints and docstring
                - Return correct data type (list/tuple/set as specified)
                - No external dependencies beyond standard library
                - Code must be self-contained and immediately executable""",
                context=specification_contract,
                max_retries=3
            ) for strategy in code_strategies]
        )

        # Step 5: Revise candidates based on specification compliance
        revised_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve this code implementation:
                - Ensure 100% compliance with specification contract
                - Add missing edge case handling
                - Fix type mismatches (return list vs tuple vs set)
                - Improve variable names and code clarity
                - Add comments for complex logic
                - Ensure no off-by-one errors in loops
                - Validate input types and lengths
                - Handle empty/single-element edge cases explicitly

                SPECIFICATION CONTRACT:
                {specification_contract}""",
                context=candidate
            ) for candidate in code_candidates]
        )

        # Step 6: Ensemble final selection with fallback to reference if available
        final_code = await self.ensemble(
            instruction="""Select the best implementation:
            - Prioritize correctness over elegance
            - Choose implementation that handles most edge cases
            - Prefer solutions with explicit error handling
            - Favor code that matches reference solution pattern if available
            - Ensure exact function signature and return type
            - If all candidates have flaws, synthesize a hybrid solution
            - Final output must be ONLY the function implementation with imports""",
            contexts_list=revised_candidates
        )

        # Step 7: Final cleanup and formatting
        cleaned_code = await self.revise(
            instruction="""Final cleanup:
            - Remove any explanatory text, only keep code
            - Ensure imports are at top of function scope
            - Match exact function name and parameters
            - Remove any print statements or debug code
            - Ensure proper indentation and PEP8 compliance
            - Return ONLY the function implementation block""",
            context=final_code
        )

        return cleaned_code