# Workflow ID: mbppplus_85_0
# Benchmark: mbppplus
# Data Indices: [350, 340]

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
        """
        Universal workflow for programming problem solving domain.
        This workflow dynamically adapts to problem type and generates robust solutions.
        """
        import asyncio
        import re
        
        # Step 1: Extract comprehensive problem semantics
        semantics_instruction = """
        Analyze the programming problem and extract the following structured information:
        1. INPUT STRUCTURE: What data types and structures are provided as input? (lists, tuples, strings, numbers, etc.)
        2. OUTPUT REQUIREMENTS: What should be returned? (specific data type, format, constraints)
        3. PROCESSING PATTERN: How should inputs be processed? (element-wise, sequential, conditional, mathematical, etc.)
        4. TERMINATION CONDITIONS: When should processing stop? (end of list, specific condition met, etc.)
        5. EDGE CASES: What edge cases must be handled? (empty inputs, single elements, boundary values, etc.)
        6. OPERATION SEMANTICS: What specific operations need to be performed? (max, min, count, filter, transform, etc.)
        7. CONSTRAINTS: Any additional constraints or requirements mentioned?
        
        Format your response as a structured JSON-like dictionary with these exact keys.
        Be thorough and precise - this analysis will guide all subsequent steps.
        """
        
        problem_semantics = await self.generate(
            instruction=semantics_instruction,
            context=""
        )
        
        # Step 2: Classify problem type to determine implementation strategy
        classification_instruction = f"""
        Based on the extracted problem semantics:
        {problem_semantics}
        
        Classify this problem into one of these categories:
        1. ELEMENT_WISE: Processing corresponding elements from multiple collections (like zip operations)
        2. SEQUENTIAL_CONDITIONAL: Processing elements in sequence until a condition is met (like counting until tuple)
        3. TRANSFORMATION: Converting or transforming data from one form to another
        4. FILTERING: Selecting elements based on conditions
        5. MATHEMATICAL: Performing mathematical operations or calculations
        6. OTHER: Doesn't fit above categories
        
        Also identify:
        - Primary operation needed (max, min, count, sum, etc.)
        - Data structure handling requirements (preserve order, remove duplicates, etc.)
        - Any special considerations
        
        Return classification as: "CATEGORY: [category], OPERATION: [operation], NOTES: [additional notes]"
        """
        
        problem_classification = await self.generate(
            instruction=classification_instruction,
            context=problem_semantics
        )
        
        # Step 3: Generate multiple solution attempts in parallel based on classification
        async def generate_solution_attempt(strategy_hint):
            code_instruction = f"""
            Generate Python code to solve the problem based on this analysis:
            Problem Semantics: {problem_semantics}
            Classification: {problem_classification}
            
            Strategy Hint: {strategy_hint}
            
            Requirements:
            - Use the exact function signature specified in the problem
            - Handle all identified edge cases (empty inputs, single elements, etc.)
            - Return the correct data type (list, tuple, set, etc.)
            - Include necessary imports at the top of the function
            - Write clean, readable code with appropriate variable names
            - Ensure type consistency and proper error handling
            - Optimize for correctness first, then efficiency
            
            Focus particularly on robustness - your solution must handle all edge cases mentioned in the problem semantics.
            """
            
            return await self.programmer(
                instruction=code_instruction,
                context=""
            )
        
        # Create different strategy hints based on classification
        strategy_hints = [
            "Use a direct, straightforward approach with clear variable names and comments",
            "Optimize for edge case handling - explicitly check for empty inputs, single elements, etc.",
            "Consider alternative implementations that might be more robust or efficient",
            "Focus on type safety and ensure proper handling of all data types mentioned"
        ]
        
        # Generate solutions in parallel
        solution_attempts = await asyncio.gather(
            *[generate_solution_attempt(hint) for hint in strategy_hints]
        )
        
        # Step 4: Ensemble - Select and synthesize the best solution
        ensemble_instruction = f"""
        You have multiple solution attempts for this programming problem:
        
        Problem Semantics: {problem_semantics}
        Classification: {problem_classification}
        
        Evaluate each solution attempt and synthesize the best possible solution by:
        1. Identifying which solution handles edge cases most comprehensively
        2. Selecting the clearest and most readable implementation
        3. Ensuring type consistency and proper return types
        4. Verifying that all requirements from problem semantics are met
        5. Combining the best elements from different solutions if appropriate
        
        Prioritize robustness over cleverness. The solution must handle:
        - Empty inputs
        - Single element cases
        - Boundary conditions
        - Type mismatches or unexpected inputs (gracefully)
        
        Return ONLY the final Python function implementation with necessary imports.
        Do not include any explanations or markdown formatting.
        """
        
        final_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=solution_attempts
        )
        
        # Step 5: Validation loop - test and refine if needed
        max_retries = 2
        current_solution = final_solution
        
        for attempt in range(max_retries):
            try:
                # Try to extract just the function code (remove any explanatory text)
                code_match = re.search(r'