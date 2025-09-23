# Workflow ID: mgsmbn_6_0
# Benchmark: mgsmbn
# Data Indices: [51, 106]

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

        # Step 1: Problem Classification and Entity Extraction
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem. Your task is to:
            1. Classify the problem type (e.g., rate, ratio, sequential, distribution, comparison)
            2. Extract all numerical values and their semantic roles (what they represent)
            3. Identify the unknown (what needs to be calculated)
            4. Note any units (টাকা, ঘণ্টা, জিনিস, etc.) and preserve them
            5. List explicit and implicit constraints (e.g., no negative people, whole numbers only)
            6. Determine if the problem requires single-step or multi-step reasoning
            7. Suggest the most appropriate solution strategy (direct calculation, algebraic, proportional, etc.)
            
            Format your response as a structured JSON-like text with clear sections.""",
            context=""
        )

        # Step 2: Problem Decomposition
        decomposition = await self.decompose(
            instruction="""Break down this problem into minimal, solvable subproblems. For each subproblem:
            - Clearly state what needs to be calculated
            - Specify its dependencies (which other subproblems must be solved first)
            - Indicate the mathematical operation required
            - Preserve units and constraints
            - Ensure the final subproblem yields the answer to the original question
            
            The decomposition should handle both sequential and parallelizable steps appropriately.""",
            context=classification
        )

        # Step 3: Parallel Solution of Independent Subproblems
        async def solve_subproblem(subproblem_desc, subproblem_id):
            # First, generate a natural language solution plan
            plan = await self.generate(
                instruction=f"""For subproblem {subproblem_id}: {subproblem_desc}
                Create a detailed step-by-step solution plan:
                - What formula or operation to use
                - Which values to plug in (with units)
                - How to handle constraints
                - Expected output format
                - Validation criteria (how to check if result makes sense)""",
                context=classification
            )
            
            # Then execute via programmer for precision
            result = await self.programmer(
                instruction=f"""Implement and execute the solution for subproblem {subproblem_id}.
                Use the plan: {plan}
                Requirements:
                - Use precise arithmetic (handle decimals/fractions correctly)
                - Validate unit consistency
                - Check against constraints (e.g., non-negative, integer if required)
                - Return only the numerical result with no text
                - If error occurs, return 'ERROR'""",
                context=plan
            )
            return {"id": subproblem_id, "result": result, "plan": plan}

        # Execute subproblems in topological order (respecting dependencies)
        solved = {}
        remaining = {sp["id"]: sp for sp in decomposition}
        
        while remaining:
            # Find subproblems with all dependencies satisfied
            ready = []
            for sp_id, sp in remaining.items():
                deps = sp.get("dependencies", "").split(",") if sp.get("dependencies") else []
                if all(dep.strip() in solved for dep in deps if dep.strip()):
                    ready.append(sp)
            
            if not ready:
                break  # Circular dependency or missing info
            
            # Solve ready subproblems in parallel
            tasks = [solve_subproblem(sp["description"], sp["id"]) for sp in ready]
            results = await asyncio.gather(*tasks)
            
            for res in results:
                solved[res["id"]] = res["result"]
                del remaining[res["id"]]

        # Step 4: Synthesize Final Answer
        synthesis_context = "\n".join([f"Subproblem {k}: {v}" for k, v in solved.items()])
        
        synthesized = await self.generate(
            instruction=f"""Synthesize the final answer from these subproblem results:
            {synthesis_context}
            
            Steps:
            1. Verify that all subproblems were solved successfully (no 'ERROR' results)
            2. Combine results according to the original problem's requirements
            3. Ensure the final answer matches the question asked
            4. Validate against real-world constraints (e.g., no fractional people if context implies whole persons)
            5. Output ONLY the final numerical answer, no units or text""",
            context=classification + "\n\n" + synthesis_context
        )

        # Step 5: Validation and Revision Loop
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                Proposed Answer: {synthesized}
                
                Check:
                1. Does it answer the original question?
                2. Are all calculations mathematically sound?
                3. Are units handled consistently?
                4. Does it respect real-world constraints?
                5. Is the magnitude reasonable? (e.g., not 1000 teachers for 60 students)
                
                If any issue is found, describe it specifically. Otherwise, respond 'VALID'.""",
                context=classification + "\n\n" + synthesis_context
            )
            
            if "VALID" in validation:
                break
                
            # Revise if invalid
            synthesized = await self.revise(
                instruction=f"""Revise the solution based on this validation feedback:
                {validation}
                
                Requirements:
                - Fix identified errors
                - Maintain numerical precision
                - Preserve unit consistency
                - Output ONLY the corrected numerical answer""",
                context=synthesized
            )

        # Step 6: Final Extraction and Formatting
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below.
            - Remove any units, text, or explanations
            - If multiple numbers, select the one that directly answers the original question
            - Ensure it's in decimal or integer form as appropriate
            - No rounding unless explicitly required by problem
            - Output must be a single number string""",
            context=synthesized
        )

        return final_answer