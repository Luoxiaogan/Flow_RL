# Workflow ID: mgsmbn_38_0
# Benchmark: mgsmbn
# Data Indices: [62, 23]

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

        # Step 1: Parallel preprocessing - classify, extract entities, detect operations
        classification_task = self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify it using this framework:
            1. Problem Type: Sequential State Change / Proportional Reasoning / Multi-Agent Estimation / Distribution / Comparison
            2. Key Entities: List all people, objects, or quantities involved with their initial values
            3. Operations: Identify all mathematical actions (add, subtract, multiply, divide, percentage, ratio) and their triggers in the text
            4. Units: Extract all units (টাকা, ঘণ্টা, জিনিস, etc.) and ensure they're consistently tracked
            5. Unknown: Precisely state what is being asked for in the question
            6. Constraints: Note any real-world constraints (non-negative, integer-only, etc.)
            Format your response with clear section headers for each category.""",
            context=""
        )

        decomposition_task = self.decompose(
            instruction="""Break down the problem into minimal, independent subproblems. Each subproblem should:
            - Represent a single calculable step or decision point
            - Have clearly defined inputs and expected outputs
            - Include any dependencies on other subproblems
            - Preserve unit information and entity tracking
            Return as a list of dictionaries with 'id', 'description', and 'dependencies' keys.""",
            context=""
        )

        # Run in parallel for efficiency
        classification, decomposition = await asyncio.gather(classification_task, decomposition_task)

        # Step 2: Validate and refine decomposition based on classification
        refined_decomposition = await self.revise(
            instruction=f"""Refine the decomposition using the classification analysis:
            Classification Context:
            {classification}

            Ensure each subproblem:
            - Matches the identified problem type (e.g., if proportional, include ratio setup)
            - Tracks units consistently throughout
            - Respects real-world constraints mentioned
            - Sequences operations in chronological/logical order
            - Explicitly states what mathematical operation is needed
            Return the refined list of subproblems in the same dictionary format.""",
            context=str(decomposition)
        )

        # Step 3: Solve each subproblem - parallelize independent ones
        # Parse the decomposition (assuming it's a list of dicts as string)
        try:
            # Simple parsing - in practice, might need json.loads or more robust parsing
            subproblems = eval(refined_decomposition) if isinstance(refined_decomposition, str) else refined_decomposition
        except:
            # Fallback: treat as string and split by likely separators
            subproblems = []
            for line in str(refined_decomposition).split('\n'):
                if 'id' in line and 'description' in line:
                    # Crude extraction - in production, use proper serialization
                    subproblems.append({
                        'id': line.split('id')[1].split(':')[0] if 'id' in line else 'unknown',
                        'description': line,
                        'dependencies': ''
                    })

        # Group subproblems by dependencies for sequential solving
        solved_subproblems = {}
        remaining_subproblems = subproblems.copy()

        while remaining_subproblems:
            # Find subproblems with all dependencies satisfied
            ready_subproblems = [
                sp for sp in remaining_subproblems 
                if all(dep.strip() in solved_subproblems for dep in sp.get('dependencies', '').split(',') if dep.strip())
            ]
            
            if not ready_subproblems:
                # Circular dependency or parsing error - break
                break

            # Solve ready subproblems in parallel
            solve_tasks = []
            for sp in ready_subproblems:
                task = self.programmer(
                    instruction=f"""Solve this subproblem with extreme precision:
                    Subproblem: {sp['description']}
                    Context from classification: {classification}
                    Previously solved subproblems: {list(solved_subproblems.items())}
                    
                    Requirements:
                    - Generate executable Python code that computes the answer
                    - Include unit tracking in variable names (e.g., stickers_count, taka_amount)
                    - Validate against real-world constraints (no negative quantities, etc.)
                    - Return only the numerical result, no text
                    - If uncertain, return 'UNCERTAIN'""",
                    context=""
                )
                solve_tasks.append(task)
            
            # Execute in parallel
            results = await asyncio.gather(*solve_tasks)
            
            # Store results
            for i, sp in enumerate(ready_subproblems):
                solved_subproblems[sp['id']] = results[i]
                remaining_subproblems.remove(sp)

        # Step 4: Synthesize final answer from solved subproblems
        synthesis_context = f"""
        Classification: {classification}
        Solved Subproblems: {solved_subproblems}
        Original Decomposition: {refined_decomposition}
        """

        final_answer = await self.programmer(
            instruction=f"""Synthesize the final answer from solved subproblems:
            {synthesis_context}
            
            Generate Python code that:
            1. Combines the results of solved subproblems logically
            2. Performs any final calculations needed
            3. Validates the answer against problem constraints
            4. Outputs ONLY the final numerical answer (integer or decimal)
            5. If any subproblem returned 'UNCERTAIN', attempt to resolve it using other subproblem results
            
            Example code structure:
            # Use solved subproblem results
            result1 = [value from subproblem 1]
            result2 = [value from subproblem 2]
            final_answer = result1 + result2  # or whatever operation is needed
            print(final_answer)""",
            context=""
        )

        # Step 5: Verify answer plausibility
        verification = await self.revise(
            instruction=f"""Critically verify the final answer:
            Final Answer: {final_answer}
            Problem Context: {self.problem_text}
            Classification: {classification}
            
            Check:
            1. Does the answer make real-world sense? (e.g., no negative stickers)
            2. Are units consistent throughout?
            3. Does it match the scale of numbers in the problem?
            4. Is it mathematically consistent with the operations described?
            
            If any issue is found, return a corrected numerical answer. Otherwise, return the original answer unchanged.""",
            context=str(final_answer)
        )

        # Extract numerical answer from verification result
        # Look for numbers in the response
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', str(verification))
        if numbers:
            return float(numbers[0]) if '.' in numbers[0] else int(numbers[0])
        else:
            # Fallback to original final answer
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', str(final_answer))
            if numbers:
                return float(numbers[0]) if '.' in numbers[0] else int(numbers[0])
            else:
                return 0  # Ultimate fallback