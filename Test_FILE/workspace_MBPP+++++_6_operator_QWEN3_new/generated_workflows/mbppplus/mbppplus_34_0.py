# Workflow ID: mbppplus_34_0
# Benchmark: mbppplus
# Data Indices: [320, 61]

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
        
        # PHASE 1: PARALLEL PROBLEM ANALYSIS - Generate multiple perspectives
        problem_analysis_tasks = [
            self.generate(
                instruction="""Analyze this programming problem from a DATA STRUCTURE perspective:
                - What is the input data type? (list, tuple, dict, set, nested?)
                - What is the output data type?
                - What structural transformations are implied? (partitioning, sorting, filtering, mapping?)
                - Are there constraints on order, mutability, or duplication?
                - What edge cases are suggested by the examples? (empty, single element, irregular sizes?)
                Provide a concise, structured analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an ALGORITHMIC OPERATION perspective:
                - What core operation is being performed? (chunking, sorting, searching, reducing, etc.)
                - What is the transformation rule? (e.g., "group every N elements", "sort each sublist")
                - Are there mathematical or logical constraints? (divisibility, ordering, uniqueness)
                - What computational pattern does this resemble? (map, reduce, sliding window, etc.)
                - What libraries or built-ins might be relevant?
                Provide a concise, structured analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an EDGE CASE & ROBUSTNESS perspective:
                - What are 3-5 edge cases not explicitly shown in examples?
                - How should empty inputs be handled?
                - What about single-element inputs?
                - Are there type coercion risks? (e.g., tuple vs list)
                - What boundary conditions exist? (N=0, N>len(data), negative numbers, etc.)
                - Should the solution preserve order? Handle duplicates?
                Provide a concise, structured analysis.""",
                context=""
            )
        ]
        
        analysis_results = await asyncio.gather(*problem_analysis_tasks)
        
        # PHASE 2: SYNTHESIZE INTO UNIFIED PROBLEM SPEC
        unified_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, comprehensive problem specification:
            - Combine data structure, algorithmic, and edge case insights
            - Identify the core transformation pattern
            - List ALL critical constraints and edge cases
            - Specify expected input/output types precisely
            - Highlight any potential pitfalls or ambiguities
            Format as a clear, structured specification that can guide code generation.""",
            contexts_list=analysis_results
        )
        
        # PHASE 3: GENERATE ALGORITHM DRAFT
        algorithm_draft = await self.generate(
            instruction=f"""Based on this unified problem specification:
            {unified_spec}
            
            Generate a step-by-step algorithm in plain English to solve this problem:
            - Use clear, imperative language ("Step 1: ...", "Step 2: ...")
            - Include explicit handling of all edge cases identified
            - Specify data type conversions if needed
            - Mention any built-in functions or libraries to use
            - Keep it language-agnostic (not Python-specific yet)""",
            context=unified_spec
        )
        
        # PHASE 4: REVISE ALGORITHM FOR ROBUSTNESS
        robust_algorithm = await self.revise(
            instruction="""Revise this algorithm to ensure maximum robustness:
            - Add explicit steps for handling empty inputs
            - Add steps for single-element edge cases
            - Ensure type consistency (e.g., returning tuple vs list)
            - Add validation steps if input constraints exist
            - Consider performance implications for large inputs
            - Add fallback behavior for unexpected inputs
            Return the complete revised algorithm.""",
            context=algorithm_draft
        )
        
        # PHASE 5: ITERATIVE CODE GENERATION WITH VALIDATION
        code_attempt = None
        max_retries = 3
        confidence = "low"
        
        for attempt in range(max_retries):
            # Generate code
            code_result = await self.programmer(
                instruction=f"""Implement this algorithm as a Python function:
                {robust_algorithm}
                
                Requirements:
                - Use EXACT function name and signature from problem
                - Include necessary imports
                - Handle ALL edge cases mentioned
                - Match return type exactly (list, tuple, dict, etc.)
                - Write clean, efficient, readable code
                - No wrapper functions or classes - only the implementation""",
                context=robust_algorithm,
                max_retries=1
            )
            
            # Extract just the code block
            code_match = re.search(r'