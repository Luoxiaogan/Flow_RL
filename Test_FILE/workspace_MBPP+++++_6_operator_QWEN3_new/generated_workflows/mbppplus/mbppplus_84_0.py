# Workflow ID: mbppplus_84_0
# Benchmark: mbppplus
# Data Indices: [80, 39]

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
        import math

        # Step 1: Parallel classification and initial decomposition hypotheses
        classification_task = self.generate(
            instruction="""Analyze the problem and classify it with extreme precision:
            1. Primary category: Is this primarily a mathematical, string manipulation, logical, or data structure problem?
            2. Secondary traits: Does it involve recursion, iteration, pattern matching, or edge case handling?
            3. Expected output type: What data type should the solution return (int, str, list, tuple, etc.)?
            4. Key operations: What core operations are needed (e.g., regex, loops, mathematical functions)?
            5. Edge cases: What edge cases must be handled (empty inputs, zeros, negatives, duplicates, etc.)?
            Format your response as a structured JSON-like summary.""",
            context=""
        )

        decomposition_hypotheses = await asyncio.gather(
            self.decompose(
                instruction="""Decompose the problem into minimal, executable subproblems. Focus on algorithmic steps.
                Each subproblem should be atomic and have clear input/output. Specify dependencies if any.
                Prioritize mathematical and logical decomposition.""",
                context=""
            ),
            self.decompose(
                instruction="""Decompose the problem with emphasis on string and pattern operations.
                Assume regex or text processing may be involved. Break into steps like: identify pattern, transform, validate.
                Specify dependencies if any.""",
                context=""
            ),
            self.decompose(
                instruction="""Decompose the problem into data structure and iteration-focused steps.
                Consider list comprehensions, set operations, or tuple manipulations. Specify dependencies if any.""",
                context=""
            )
        )

        # Step 2: Ensemble to select best decomposition
        decomposition_jsons = [
            str(hyp) for hyp in decomposition_hypotheses
        ]
        best_decomposition = await self.ensemble(
            instruction="""Select the most coherent, complete, and appropriate decomposition for this problem.
            Consider:
            - Alignment with problem classification (e.g., if classified as string problem, prefer regex decomposition)
            - Completeness of steps (no missing dependencies)
            - Feasibility of implementation
            - Handling of edge cases
            Return the selected decomposition as a Python list of dictionaries with 'id', 'description', 'dependencies'.""",
            contexts_list=decomposition_jsons
        )

        # Step 3: Extract and parse decomposition
        # Use Programmer to safely parse the decomposition into executable structure
        parsed_decomposition = await self.programmer(
            instruction="""Parse the decomposition text into a Python list of subproblem dictionaries.
            Each dictionary must have: 'id' (string), 'description' (string), 'dependencies' (comma-separated string or empty).
            If the input is not valid, return an empty list. Do not execute any logic beyond parsing.
            Example output: [{'id': 'step1', 'description': 'Check divisibility by 2', 'dependencies': ''}]""",
            context=best_decomposition
        )

        # Step 4: Execute subproblems in dependency order
        results = {}
        subproblems = eval(parsed_decomposition) if parsed_decomposition.strip() else []
        
        # Build dependency graph and execute in order
        executed_ids = set()
        remaining_subproblems = subproblems.copy()

        for _ in range(len(subproblems) + 5):  # Safety limit
            if not remaining_subproblems:
                break
                
            current_batch = []
            for sp in remaining_subproblems[:]:
                deps = [d.strip() for d in sp['dependencies'].split(',')] if sp['dependencies'] else []
                if all(dep in executed_ids for dep in deps) or not deps:
                    current_batch.append(sp)
                    remaining_subproblems.remove(sp)
            
            if not current_batch:
                # Circular dependency or missing deps - break
                break
                
            # Execute batch in parallel
            batch_tasks = []
            for sp in current_batch:
                # Route to appropriate operator based on description
                if any(kw in sp['description'].lower() for kw in ['compute', 'calculate', 'math', 'number', 'divisor', 'prime']):
                    task = self.programmer(
                        instruction=f"""Implement this subproblem with extreme attention to edge cases:
                        Subproblem: {sp['description']}
                        Context from previous steps: {str(results)}
                        Classification context: {classification_task}
                        Requirements:
                        - Handle all edge cases mentioned in classification
                        - Return result in correct data type
                        - Include necessary imports (math, etc.) if needed
                        - Code must be self-contained and runnable""",
                        context=str(results)
                    )
                elif any(kw in sp['description'].lower() for kw in ['string', 'text', 'pattern', 'regex', 'parenthesis', 'remove']):
                    task = self.programmer(
                        instruction=f"""Implement this string subproblem:
                        Subproblem: {sp['description']}
                        Context from previous steps: {str(results)}
                        Classification context: {classification_task}
                        Requirements:
                        - Use regex if appropriate (import re)
                        - Handle edge cases like empty strings, nested parens
                        - Preserve data types (return str, not list)
                        - Code must be self-contained""",
                        context=str(results)
                    )
                else:
                    # Default to generate for logical/data structure problems
                    task = self.generate(
                        instruction=f"""Solve this subproblem through logical reasoning:
                        Subproblem: {sp['description']}
                        Context from previous steps: {str(results)}
                        Classification: {classification_task}
                        Return only the final result in the expected format.""",
                        context=str(results)
                    )
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Store results by subproblem ID
            for i, sp in enumerate(current_batch):
                results[sp['id']] = batch_results[i]
                executed_ids.add(sp['id'])

        # Step 5: Synthesize final result
        final_result = await self.ensemble(
            instruction="""Synthesize the final answer from subproblem results.
            Consider:
            - The original problem's expected output format
            - Any remaining transformations needed
            - Validation against edge cases from classification
            Return ONLY the final result in the exact format required (no explanations).""",
            contexts_list=[str(results), classification_task]
        )

        # Step 6: Validate and revise if necessary (self-correction loop)
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this result against the original problem:
                Result: {final_result}
                Problem: {self.problem_text}
                Check for:
                - Correct data type
                - Edge case handling
                - Format compliance
                - Logical consistency
                If valid, return 'VALID'. If invalid, return specific error message.""",
                context=final_result
            )
            
            if "VALID" in validation:
                break
                
            # Revise with error context
            final_result = await self.revise(
                instruction=f"""Revise the solution to fix this specific error:
                Error: {validation}
                Previous result: {final_result}
                Classification context: {classification_task}
                Return ONLY the corrected result in required format.""",
                context=final_result
            )
        else:
            # If all attempts fail, return best effort
            pass

        return final_result