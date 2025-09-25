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
        self.decompose = operator.Decompose(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.selfconsistency = operator.SelfConsistency(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio

        # Step 1: Extract function name and understanding
        func_name = await self.generate(
            instruction="Extract the function name from the test cases. Return ONLY the function name, nothing else.",
            context=self.problem_text
        )

        # Step 2: Analyze the task description
        task_analysis = await self.generate(
            instruction=f"""
            Given the task description and test cases:
            {self.problem_text}

            Analyze and fully understand the requirements. 
            Identify the key operations, edge cases, and constraints that must be handled.
            Ensure that the function signature matches exactly with the test cases.
            Provide a detailed breakdown of the logic and steps required to solve the problem.
            """,
            context=self.problem_text
        )

        # Step 3: Generate multiple code solutions in parallel
        solution1 = await self.generate(
            instruction=f"""
            Based on the following detailed analysis:
            {task_analysis}

            Write a Python function named {func_name} that solves the problem described.
            Ensure that the function includes all necessary imports and handles edge cases.
            Follow the format:
            def {func_name}(...):
                # implementation
                return ...
            """,
            context=self.problem_text
        )

        solution2 = await self.generate(
            instruction=f"""
            Based on the following detailed analysis:
            {task_analysis}

            Write a Python function named {func_name} that solves the problem described.
            Ensure that the function includes all necessary imports and handles edge cases.
            Follow the format:
            def {func_name}(...):
                # implementation
                return ...
            """,
            context=self.problem_text
        )

        solution3 = await self.generate(
            instruction=f"""
            Based on the following detailed analysis:
            {task_analysis}

            Write a Python function named {func_name} that solves the problem described.
            Ensure that the function includes all necessary imports and handles edge cases.
            Follow the format:
            def {func_name}(...):
                # implementation
                return ...
            """,
            context=self.problem_text
        )

        # Step 4: Use SelfConsistency to select the best solution
        best_solution = await self.selfconsistency(
            instruction=f"""
            Evaluate the following three Python function implementations:
            
            Solution 1:
            {solution1}
            
            Solution 2:
            {solution2}
            
            Solution 3:
            {solution3}

            Select the best solution based on consistency, logical correctness, and completeness.
            Ensure the selected solution adheres strictly to the test cases and task description.
            Return the best solution as the final output.
            """,
            context=self.problem_text
        )

        return best_solution