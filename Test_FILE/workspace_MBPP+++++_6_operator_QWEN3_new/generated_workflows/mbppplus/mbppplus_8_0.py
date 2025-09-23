# Workflow ID: mbppplus_8_0
# Benchmark: mbppplus
# Data Indices: [29, 119]

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

        # Phase 1: Decompose the problem into structural constraints and subproblems
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its fundamental components:
            1. Identify exact input types and structures (e.g., tuple of ints, list of strings)
            2. Identify exact output types and structures (must match test case expectations)
            3. Extract transformation pattern from test cases (how input maps to output)
            4. List all edge cases implied or possible (empty inputs, single elements, boundaries)
            5. Note any invariants (order preservation, uniqueness, type consistency)
            6. Infer the core operation (filtering, mapping, combining, generating, etc.)
            Return as structured subproblems with clear IDs and dependencies.""",
            context=""
        )

        # Summarize decomposition for efficient context passing
        decomposition_summary = await self.summarize(
            instruction="""Condense the problem decomposition into a concise specification:
            - Input type: [type]
            - Output type: [type]
            - Core operation: [description]
            - Key edge cases: [list]
            - Critical constraints: [list]
            Format as bullet points for easy consumption by code generators.""",
            context=str(decomposition)
        )

        # Phase 2: Generate multiple solution candidates in parallel
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a Python function solution based on this specification:
                {decomposition_summary}
                
                Approach 1: Literal pattern extraction
                - Study test cases as concrete input-output examples
                - Derive transformation rules directly from examples
                - Prioritize exact replication of test case behavior
                - Handle edge cases explicitly as identified in decomposition""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function solution based on this specification:
                {decomposition_summary}
                
                Approach 2: Abstract algorithm design
                - Ignore specific test values, focus on general transformation
                - Design algorithm using appropriate data structures and operations
                - Ensure type safety and contract adherence
                - Include defensive programming for edge cases""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function solution based on this specification:
                {decomposition_summary}
                
                Approach 3: Type-aware structural manipulation
                - Focus on precise type conversions (tuple/list/dict/set)
                - Use Python's built-in functions and comprehensions efficiently
                - Preserve order/structure as required
                - Minimalist implementation focused on core operation""",
                context=""
            )
        ]
        
        candidates = await asyncio.gather(*candidate_tasks)

        # Phase 3: Validate and synthesize
        # First, generate validation logic for each candidate
        validation_tasks = [
            self.programmer(
                instruction=f"""Given this candidate solution and problem specification:
                Specification: {decomposition_summary}
                
                Write comprehensive test assertions that verify:
                - Correctness on provided test cases
                - Handling of all identified edge cases
                - Type consistency (input/output types match exactly)
                - No side effects or global state
                Output ONLY the assertion code, no explanations.""",
                context=candidate
            ) for candidate in candidates
        ]
        
        validations = await asyncio.gather(*validation_tasks)

        # Revise candidates based on validation feedback
        revised_candidates = []
        for i, (candidate, validation) in enumerate(zip(candidates, validations)):
            revised = await self.revise(
                instruction=f"""Improve this solution based on validation feedback:
                Original candidate: {candidate}
                Validation assertions: {validation}
                
                Fix any discrepancies between implementation and validation.
                Ensure function signature matches exactly.
                Handle all edge cases mentioned in decomposition.
                Output ONLY the corrected Python function with imports inside.""",
                context=candidate
            )
            revised_candidates.append(revised)

        # Final synthesis: ensemble selects and merges best elements
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            - Select the candidate with most comprehensive edge case handling
            - If multiple are strong, merge their strengths (e.g., take core logic from one, edge case handling from another)
            - Ensure output is EXACTLY a Python function with correct signature
            - Include necessary imports inside the function if any
            - NO markdown, NO explanations, ONLY code
            - Must pass all validation assertions provided""",
            contexts_list=revised_candidates
        )

        return final_solution