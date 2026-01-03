# Workflow ID: mgsmbn_96_0
# Benchmark: mgsmbn
# Data Indices: [111]

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

        # STEP 1: Problem DNA Extraction - Comprehensive semantic analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math word problem. Extract and structure the following:
            1. ALL known numerical values with their units and contextual meaning (e.g., "27 unicorns total")
            2. The specific unknown being asked for (the target answer)
            3. Mathematical relationships (ratios, fractions, operations implied)
            4. Entities involved (people, objects, groups) and their quantities
            5. Temporal or logical sequence of events (if any)
            6. Problem classification: rate, proportion, distribution, comparison, multi-step, etc.
            7. Any implicit constraints (e.g., "must be integer", "positive only")
            8. Potential pitfalls or ambiguities in interpretation
            
            Format as a structured JSON-like text with clear section headers.""",
            context=""
        )

        # STEP 2: Problem Complexity Classification
        complexity_analysis = await self.generate(
            instruction=f"""Based on the following analysis:
            {problem_analysis}
            
            Classify this problem's complexity and recommend solution strategy:
            - SIMPLE: Single operation, no hidden steps, direct calculation
            - MULTI_STEP: Requires 2+ sequential calculations with dependencies
            - AMBIGUOUS: Unclear relationships, missing information, or multiple interpretations
            - COMPLEX: Requires algebraic reasoning, unit conversions, or advanced proportional thinking
            
            Also estimate the number of distinct calculation steps required.
            
            Finally, recommend whether to use: 
            A) Direct Programmer execution
            B) Hierarchical decomposition
            C) Parallel solution approaches with ensemble verification
            
            Justify your classification and recommendation in 3-5 sentences.""",
            context=problem_analysis
        )

        # STEP 3: Conditional Branching based on complexity
        if "SIMPLE" in complexity_analysis and "A)" in complexity_analysis:
            # Direct solution path for simple problems
            direct_solution = await self.programmer(
                instruction=f"""Solve this Bengali math problem directly using precise calculation:
                Problem Analysis: {problem_analysis}
                
                Requirements:
                - Show all calculation steps clearly
                - Maintain unit consistency throughout
                - Round appropriately (integer if context implies discrete entities)
                - Final answer must be a single numerical value
                - Double-check arithmetic for errors""",
                context=problem_analysis
            )
            
            # Quick verification
            verified_solution = await self.revise(
                instruction="""Verify this solution:
                1. Does the answer match the question asked?
                2. Are units consistent and appropriate?
                3. Is the result plausible in real-world context?
                4. Any calculation errors?
                
                If any issues, correct them. Otherwise, extract only the final numerical answer.""",
                context=direct_solution
            )
            
            return verified_solution

        else:
            # STEP 4: Hierarchical Decomposition for complex problems
            decomposition = await self.decompose(
                instruction=f"""Break down this problem into minimal, solvable subproblems:
                Problem Analysis: {problem_analysis}
                Complexity Assessment: {complexity_analysis}
                
                Create subproblems that:
                - Each can be solved independently once dependencies are met
                - Have clear inputs and expected outputs
                - Maintain unit consistency
                - Follow logical/chronological order
                - Include any necessary intermediate calculations
                
                For each subproblem, specify:
                - What needs to be calculated
                - What inputs it requires (from problem or other subproblems)
                - What mathematical operation(s) to apply
                - Any unit conversions or constraints
                
                Ensure dependencies are correctly specified.""",
                context=f"{problem_analysis}\n\n{complexity_analysis}"
            )

            # STEP 5: Solve subproblems in dependency order
            solved_subproblems = {}
            
            # Get all subproblem IDs
            subproblem_ids = [sp['id'] for sp in decomposition]
            
            # Solve in topological order (respecting dependencies)
            remaining_subproblems = decomposition.copy()
            
            for _ in range(len(decomposition) + 2):  # Safety limit
                progress_made = False
                current_batch = []
                
                for sp in remaining_subproblems[:]:
                    deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                    deps = [d.strip() for d in deps if d.strip()]
                    
                    # Check if all dependencies are solved
                    if all(dep in solved_subproblems for dep in deps):
                        current_batch.append(sp)
                        remaining_subproblems.remove(sp)
                        progress_made = True
                
                if not current_batch:
                    break  # No progress, break to avoid infinite loop
                
                # Solve current batch in parallel
                async def solve_subproblem(sp):
                    deps_context = "\n".join([f"Subproblem {dep}: {solved_subproblems[dep]}" for dep in deps if dep in solved_subproblems])
                    
                    solution = await self.programmer(
                        instruction=f"""Solve this subproblem:
                        {sp['description']}
                        
                        Context from dependencies:
                        {deps_context}
                        
                        Problem Analysis: {problem_analysis}
                        
                        Requirements:
                        - Show calculation steps
                        - Maintain units
                        - Be precise
                        - Return only the numerical result with unit if applicable""",
                        context=f"Subproblem: {sp['description']}\nDependencies: {deps_context}"
                    )
                    
                    # Verify subproblem solution
                    verified = await self.revise(
                        instruction="""Verify this subproblem solution:
                        1. Correct calculation?
                        2. Units consistent?
                        3. Matches expected type (integer/decimal)?
                        4. Plausible given context?
                        
                        If errors, fix them. Return only the final numerical value.""",
                        context=solution
                    )
                    
                    return sp['id'], verified
                
                # Solve batch in parallel
                results = await asyncio.gather(*[solve_subproblem(sp) for sp in current_batch])
                for sp_id, result in results:
                    solved_subproblems[sp_id] = result
            
            # STEP 6: Parallel Verification Paths
            # Path 1: Algorithmic solution (already have from above)
            final_subproblem_id = subproblem_ids[-1] if subproblem_ids else ""
            algorithmic_answer = solved_subproblems.get(final_subproblem_id, "")
            
            # Path 2: Narrative solution (explain in Bengali-style reasoning)
            narrative_solution = await self.generate(
                instruction=f"""Explain the solution to this problem in clear, step-by-step Bengali narrative style, as if teaching a student:
                Problem Analysis: {problem_analysis}
                Subproblem Solutions: {json.dumps(solved_subproblems, indent=2)}
                
                Requirements:
                - Use simple language
                - Show each calculation step with reasoning
                - Explain why each step is necessary
                - Conclude with the final answer
                - The final answer should be clearly stated at the end""",
                context=f"{problem_analysis}\n\nSubproblem Solutions: {solved_subproblems}"
            )
            
            # Path 3: Critical review for plausibility
            critical_review = await self.revise(
                instruction=f"""Critically review this solution for real-world plausibility and mathematical soundness:
                Problem: {self.problem_text}
                Algorithmic Answer: {algorithmic_answer}
                Narrative Solution: {narrative_solution}
                
                Check:
                1. Does the answer make sense in context? (e.g., no negative unicorns)
                2. Are units correct and consistent?
                3. Any calculation errors in the narrative?
                4. Does the narrative match the algorithmic solution?
                5. Any hidden assumptions that need to be stated?
                
                If issues found, provide corrected answer. Otherwise, confirm the answer.""",
                context=f"Algorithmic: {algorithmic_answer}\nNarrative: {narrative_solution}"
            )
            
            # STEP 7: Ensemble Verification
            final_answer = await self.ensemble(
                instruction="""Synthesize the three solution perspectives into one definitive answer:
                1. Algorithmic solution (precise calculation)
                2. Narrative solution (step-by-step reasoning)
                3. Critical review (plausibility check)
                
                Your task:
                - If all three agree, return the consensus answer
                - If there's disagreement, identify the most reliable source and explain why
                - Extract ONLY the final numerical answer (no units, no explanation)
                - Ensure the answer is properly formatted as a number (integer or decimal)
                
                The output must be a single numerical value that directly answers the original question.""",
                contexts_list=[algorithmic_answer, narrative_solution, critical_review]
            )
            
            return final_answer