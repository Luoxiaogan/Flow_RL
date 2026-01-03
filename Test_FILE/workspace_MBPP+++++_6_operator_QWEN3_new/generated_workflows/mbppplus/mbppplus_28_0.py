# Workflow ID: mbppplus_28_0
# Benchmark: mbppplus
# Data Indices: [346, 237]

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

        # Stage 1: Deep Problem Decomposition
        decomposition = await self.decompose(
            instruction="""Break this programming problem into core semantic components:
            1. INPUT CONTRACT: What are the exact input types, formats, and constraints? 
            2. OUTPUT CONTRACT: What must be returned? Include type, structure, and edge behavior.
            3. ALGORITHMIC CORE: What fundamental operation is being asked? (e.g., min/max, counting, transformation)
            4. EDGE TRIGGERS: What input patterns would trigger edge cases? (empty, single, duplicates, boundaries)
            5. FAILURE MODES: When should the function return error values or handle impossibility?
            6. PERFORMANCE NOTES: Are there efficiency constraints or scalability concerns?
            Return as structured subproblems with clear IDs and dependency chains.""",
            context=""
        )

        # Stage 2: Parallel Reasoning Tracks
        spec_track = self.generate(
            instruction="""Based on the decomposition, create a FORMAL SPECIFICATION:
            - List all preconditions (what must be true about inputs)
            - List all postconditions (what must be true about outputs)
            - Define invariants (what remains unchanged or must be maintained)
            - Specify error handling protocol
            - Format as markdown with clear sections""",
            context=str(decomposition)
        )

        strategy_track = self.generate(
            instruction="""Propose 2-3 distinct ALGORITHMIC STRATEGIES:
            For each strategy:
            - Describe the approach in plain English
            - Estimate time/space complexity
            - List pros and cons
            - Identify which edge cases it handles naturally
            - Note any tricky implementation details
            Prioritize clarity and correctness over premature optimization.""",
            context=str(decomposition)
        )

        edge_track = self.generate(
            instruction="""Generate COMPREHENSIVE EDGE CASES:
            - Empty inputs
            - Single element inputs
            - Maximum/minimum value inputs
            - Duplicate-heavy inputs
            - Boundary condition inputs
            - Adversarial inputs (designed to break naive solutions)
            - Type boundary cases (if applicable)
            Format as a bulleted list with brief rationale for each.""",
            context=str(decomposition)
        )

        # Execute parallel tracks
        spec_result, strategy_result, edge_result = await asyncio.gather(
            spec_track, strategy_track, edge_track
        )

        # Stage 3: Synthesize into Master Specification
        master_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a SINGLE MASTER SPECIFICATION:
            1. Integrate formal contracts from spec track
            2. Select the most robust algorithmic strategy (or hybrid) from strategy track
            3. Incorporate all edge cases from edge track into validation requirements
            4. Add explicit handling instructions for each edge case
            5. Include failure mode handling from decomposition
            Output as a comprehensive, implementation-ready spec document.""",
            contexts_list=[spec_result, strategy_result, edge_result]
        )

        # Stage 4: Generate Initial Code
        initial_code = await self.programmer(
            instruction=f"""Generate Python code that strictly adheres to this master specification:
            {master_spec}
            
            CRITICAL REQUIREMENTS:
            - Use EXACT function name and signature from original problem
            - Include necessary imports inside function if needed
            - Handle ALL edge cases enumerated in spec
            - Return correct data types (list vs tuple vs set matters)
            - Include minimal but clear comments for complex logic
            - No wrapper functions or classes - just the required function""",
            context=master_spec,
            max_retries=2
        )

        # Stage 5: Adversarial Validation Loop
        current_code = initial_code
        for iteration in range(3):
            validator_prompt = f"""Act as an adversarial code reviewer. Given this implementation:
            {current_code}
            
            And this master spec:
            {master_spec}
            
            Find ALL potential flaws:
            - Logic errors (especially edge cases)
            - Type mismatches
            - Off-by-one errors
            - Unhandled failure modes
            - Efficiency issues
            - Deviations from spec
            If no flaws found, respond 'VALIDATED'.
            Otherwise, list flaws with specific line references and fixes."""
            
            validation = await self.generate(
                instruction=validator_prompt,
                context=current_code
            )
            
            if "VALIDATED" in validation.upper():
                break
                
            # Revise based on validation feedback
            current_code = await self.revise(
                instruction=f"""Fix ALL issues identified in validation:
                {validation}
                
                Maintain strict adherence to function signature and return types.
                Preserve working parts while fixing flaws.
                Add comments explaining fixes for complex changes.""",
                context=current_code
            )
        else:
            # Fallback: Generate 3 variants and ensemble if validation loop exhausted
            variant_tasks = [
                self.programmer(
                    instruction=f"""Generate implementation variant {i+1}:
                    Master Spec: {master_spec}
                    Avoid pitfalls identified in previous attempts.
                    Consider alternative algorithmic approaches.
                    Prioritize robustness over elegance.""",
                    context=master_spec,
                    max_retries=1
                ) for i in range(3)
            ]
            
            variants = await asyncio.gather(*variant_tasks)
            variants.append(current_code)  # Include last revised version
            
            current_code = await self.ensemble(
                instruction="""Select the most robust implementation from these variants:
                - Must handle all edge cases
                - Must match spec exactly
                - Prefer simpler, more readable code when correctness is equal
                - If all have flaws, synthesize a hybrid solution combining their strengths
                Return ONLY the final code with no additional text.""",
                contexts_list=variants
            )

        # Stage 6: Final Sanitization - Extract ONLY the function code
        final_extraction = await self.generate(
            instruction="""Extract ONLY the Python function code from this text:
            - Remove any explanatory text, markdown, or commentary
            - Keep ONLY the function definition and its body
            - Preserve all imports that are inside the function
            - Ensure no wrapper classes or additional functions
            - Output should be ready to execute as-is
            
            If multiple code blocks exist, select the most complete and correct one.""",
            context=current_code
        )

        return final_extraction