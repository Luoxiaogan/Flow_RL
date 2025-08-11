# Workflow ID: humaneval_0_0
# Benchmark: humaneval
# Data Indices: [0, 1]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - ALL operators return STRINGS
        - Import modules (json, re, etc.) at the beginning
        - Use detailed, comprehensive instructions
        - Parse JSON with json.loads() if needed
        """
        import asyncio
        
        # Step 1: Extract ONLY the function name from the def statement
        func_name = await self.generate(
            instruction="Extract ONLY the function name from the def statement. Return just the name, nothing else.",
            context=""
        )
        
        # Step 2: Analyze the docstring carefully — what’s the pattern? What are edge cases?
        analysis = await self.generate(
            instruction="""
            Analyze the docstring and examples carefully:
            1. What pattern do the examples show?
            2. What are the edge cases (e.g., empty input, single element, duplicates)?
            3. What is the expected return type (int, float, list, bool, etc.)?
            Return a brief analysis in 2–3 sentences.
            """,
            context=""
        )
        
        # Step 3: Generate the full implementation with precise instructions
        solution = await self.generate(
            instruction=f"""
            Implement the function '{func_name}' based on the docstring specification.
            Analysis: {analysis}
            
            Requirements:
            1. Follow the EXACT function signature provided (including types if specified)
            2. Implement the logic that satisfies ALL examples in the docstring
            3. Handle edge cases shown in examples (e.g., empty lists, single items, thresholds)
            4. Return the correct type as shown in examples (e.g., int vs float, list vs str)
            5. Include any necessary imports at the top (e.g., from typing import List)
            6. Return ONLY the Python code, no explanations or comments
            """,
            context=""
        )
        
        return solution