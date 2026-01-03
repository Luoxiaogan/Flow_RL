# Workflow ID: mgsmbn_112_0
# Benchmark: mgsmbn
# Data Indices: [41]

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
        import json

        # STEP 1: Decompose the problem into atomic, ordered subproblems
        decomposition_instruction = """
        Systematically break down this Bengali math word problem into minimal, independent calculation steps.
        For each subproblem:
        - Clearly state what needs to be calculated
        - Specify all required inputs (quantities, rates, entities)
        - Identify dependencies (which other subproblems must be solved first)
        - Preserve units and contextual constraints (e.g., no negative people)
        - Format each as a standalone computational task
        
        Example output structure:
        [
            {"id": "1", "description": "Calculate total earnings from 6 truck tires at $60 each", "dependencies": ""},
            {"id": "2", "description": "Calculate total earnings from 4 car tires at $40 each", "dependencies": ""},
            {"id": "3", "description": "Sum results of subproblems 1 and 2 to get Thursday's total", "dependencies": "1,2"}
        ]
        """
        subproblems = await self.decompose(instruction=decomposition_instruction, context="")

        # STEP 2: Solve each independent subproblem in parallel using precise code execution
        async def solve_subproblem(subproblem):
            programmer_instruction = f"""
            Generate and execute Python code to solve this EXACT subproblem:
            "{subproblem['description']}"
            
            Requirements:
            - Use exact arithmetic (fractions/decimals as needed)
            - Track units explicitly in comments
            - Validate output against real-world constraints (e.g., non-negative, integer if required)
            - Return ONLY the final numerical result as a float or int
            - If impossible or ambiguous, return "ERROR: [reason]"
            """
            result = await self.programmer(instruction=programmer_instruction, context="")
            return {"id": subproblem["id"], "result": result, "description": subproblem["description"]}

        # Group subproblems by dependency level for phased execution
        solved = {}
        max_iterations = len(subproblems)  # Safety limit
        for _ in range(max_iterations):
            # Find subproblems whose dependencies are satisfied
            ready = [
                sp for sp in subproblems 
                if all(dep.strip() in solved for dep in sp.get("dependencies", "").split(",") if dep.strip())
            ]
            if not ready:
                break  # No progress possible

            # Solve ready subproblems in parallel
            tasks = [solve_subproblem(sp) for sp in ready]
            results = await asyncio.gather(*tasks)
            
            # Store results
            for res in results:
                solved[res["id"]] = res["result"]
                if "ERROR" in str(res["result"]):
                    # Trigger revision for errored subproblems
                    revision_instruction = f"""
                    The following subproblem failed: "{res['description']}"
                    Error: {res['result']}
                    
                    Revise the problem description to resolve ambiguity or fix logical gaps.
                    Ensure it specifies:
                    - Exact quantities and units
                    - Clear mathematical operation
                    - Contextual constraints
                    Return ONLY the revised subproblem description.
                    """
                    revised_desc = await self.revise(instruction=revision_instruction, context=res["description"])
                    
                    # Retry with revised description
                    retry_instruction = programmer_instruction.replace(res["description"], revised_desc)
                    retry_result = await self.programmer(instruction=retry_instruction, context="")
                    solved[res["id"]] = retry_result

        # STEP 3: Synthesize final answer from subproblem results
        synthesis_context = "\n".join([f"Subproblem {id}: {result}" for id, result in solved.items()])
        ensemble_instruction = """
        Synthesize the subproblem results into a final numerical answer.
        Steps:
        1. Verify all subproblem results are valid numbers (no ERRORs)
        2. Apply final computation (e.g., difference, sum, ratio) as required by the original problem
        3. Validate against real-world constraints (e.g., non-negative, appropriate precision)
        4. Return ONLY the final number as a float or int
        
        If any inconsistency is found, return "REVISION_NEEDED"
        """
        final_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=[synthesis_context]
        )

        # STEP 4: Meta-validation through natural language explanation
        if "REVISION_NEEDED" not in final_answer:
            explanation_instruction = """
            Generate a step-by-step explanation in simple Bengali-appropriate terms:
            - Start from original problem
            - Show how each subproblem contributes to final answer
            - Explicitly state all operations and units
            - Conclude with final answer
            """
            explanation = await self.generate(instruction=explanation_instruction, context="")

            validation_instruction = """
            Verify that this explanation logically leads to the computed answer.
            Check:
            - All quantities match original problem
            - Operations are correctly applied
            - Units are consistent
            - Final answer matches computed result
            If valid, return "VALID". If not, return "INVALID: [reason]"
            """
            validation = await self.revise(instruction=validation_instruction, context=f"Answer: {final_answer}\n\nExplanation: {explanation}")

            if "INVALID" in validation:
                # Fallback: Direct Programmer solve with full context
                fallback_instruction = """
                Solve the original problem end-to-end with explicit step-by-step code.
                Requirements:
                - Parse Bengali text to extract all numbers and relationships
                - Perform all calculations in code
                - Validate intermediate and final results
                - Return ONLY final numerical answer
                """
                final_answer = await self.programmer(instruction=fallback_instruction, context="")

        # Extract numerical answer from string (handles "40.0", "40", etc.)
        try:
            if isinstance(final_answer, str):
                # Clean and convert
                cleaned = final_answer.strip().replace(",", "").split()[0]  # Take first token
                if "." in cleaned:
                    final_answer = float(cleaned)
                else:
                    final_answer = int(cleaned)
        except:
            # Last resort: Return 0 (should rarely happen)
            final_answer = 0

        return final_answer