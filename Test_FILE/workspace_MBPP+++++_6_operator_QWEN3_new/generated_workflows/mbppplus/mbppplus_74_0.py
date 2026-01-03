# Workflow ID: mbppplus_74_0
# Benchmark: mbppplus
# Data Indices: [314, 323]

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

        # Phase 1: Deep Problem Analysis & Constraint Extraction
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:

1. Problem Classification:
   - Is this a transformation, reduction, search, sort, or validation problem?
   - What is the core algorithmic pattern required?

2. Input/Output Specification:
   - What are the expected input types and structures?
   - What output type and format is required (list, tuple, set, scalar)?
   - Are there ordering or uniqueness constraints?

3. Behavioral Inference from Test Cases:
   - What patterns emerge from the input-output examples?
   - What edge cases are implied (empty inputs, single elements, duplicates, zeros, negatives)?
   - Are there hidden rules not explicitly stated?

4. Algorithmic Strategy:
   - What Python constructs or algorithms are most appropriate?
   - Should we use built-ins, custom functions, or mathematical operations?
   - Are there performance or complexity constraints?

5. Potential Pitfalls:
   - What are common mistakes for this type of problem?
   - What type conversions or boundary conditions might cause errors?

Structure your response clearly with numbered sections. Be exhaustive - this analysis will guide all subsequent steps.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        # Generate 3 distinct solution approaches in parallel
        solution_attempts = await asyncio.gather(
            self.programmer(
                instruction=f"""Generate a Python solution based on this analysis:
{analysis}

APPROACH 1: Direct Implementation
- Focus on simplicity and readability
- Use built-in functions where appropriate
- Handle edge cases explicitly
- Match exact return type from test cases""",
                context=analysis
            ),
            self.programmer(
                instruction=f"""Generate a Python solution based on this analysis:
{analysis}

APPROACH 2: Robust Implementation
- Focus on defensive programming
- Add type checking and input validation
- Handle all edge cases systematically
- Include comments explaining key decisions""",
                context=analysis
            ),
            self.programmer(
                instruction=f"""Generate a Python solution based on this analysis:
{analysis}

APPROACH 3: Optimized Implementation
- Focus on algorithmic efficiency
- Consider time/space complexity
- Use appropriate data structures
- Minimize unnecessary operations while maintaining correctness""",
                context=analysis
            )
        )

        # Phase 3: Solution Validation and Synthesis
        # First, extract just the code from each attempt for ensemble
        code_only_attempts = []
        for attempt in solution_attempts:
            # Extract code blocks if present
            code_blocks = re.findall(r'