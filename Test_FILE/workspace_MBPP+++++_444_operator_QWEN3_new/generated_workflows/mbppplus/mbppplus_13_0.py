# Workflow ID: mbppplus_13_0
# Benchmark: mbppplus
# Data Indices: [88, 372, 353]

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
        
        # Phase 1: Parallel diagnostic analysis
        classification_task = self.generate(
            instruction="""Analyze this programming problem comprehensively:
            1. Classify by algorithmic approach: Is this dynamic programming, greedy, string manipulation, mathematical, conditional logic, or other?
            2. Identify structural patterns: Does it require iteration, recursion, state tracking, or direct transformation?
            3. Determine return type obligations: What specific values must be returned (None, float('inf'), specific types)?
            4. List semantic constraints: What conditions trigger special returns or edge case handling?
            5. Extract key operations: What core computations or transformations are required?
            Provide structured response with clear section headers for each analysis point.""",
            context=""
        )
        
        pattern_matching_task = self.generate(
            instruction="""Identify known algorithmic patterns in this problem:
            - Map to standard algorithm templates (DP, two-pointer, sliding window, etc.)
            - Reference similar classic problems
            - Suggest optimal time/space complexity
            - Note any deceptive elements that might lead to wrong approach
            Format as bullet points with brief explanations.""",
            context=""
        )
        
        edge_case_analysis_task = self.generate(
            instruction="""Systematically identify edge cases and boundary conditions:
            - Empty inputs or zero-length cases
            - Single element cases
            - Maximum/minimum value cases
            - Cases that trigger special return values (None, inf, etc.)
            - Input type variations (if applicable)
            For each edge case, explain why it matters and how it should be handled.
            Format as numbered list with clear case descriptions and handling requirements.""",
            context=""
        )
        
        # Execute parallel analysis
        classification, pattern_matching, edge_case_analysis = await asyncio.gather(
            classification_task, pattern_matching_task, edge_case_analysis_task
        )
        
        # Phase 2: Synthesize diagnostics into unified strategy
        solving_strategy = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified solving strategy:
            1. Combine algorithmic classification with pattern matching to select primary approach
            2. Integrate edge case requirements into implementation plan
            3. Resolve any conflicts between analyses (e.g., if classification suggests DP but pattern matching suggests greedy)
            4. Create step-by-step implementation plan that addresses all constraints
            5. Specify exact function signature to implement (must match original)
            Output should be a coherent, actionable plan that a programmer could follow to implement the solution correctly.""",
            contexts_list=[classification, pattern_matching, edge_case_analysis]
        )
        
        # Phase 3: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Implement the solution based on this strategy:
            {solving_strategy}
            
            Requirements:
            - Use EXACT function signature from original problem
            - Handle all edge cases identified in analysis
            - Return correct types (None, float('inf'), etc.) as required
            - Include necessary imports at top of function
            - Write clean, efficient code with appropriate variable names
            - Do NOT include any test cases or print statements
            - Return ONLY the function implementation as specified
            
            Format your response EXACTLY as: