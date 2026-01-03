# Workflow ID: limr_25_0
# Benchmark: limr
# Data Indices: [163, 165]

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

        # Step 1: Problem Classification & Strategy Selection
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategy planning:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. List all applicable solution techniques (modular arithmetic, generating functions, coordinate geometry, etc.)
            3. Estimate complexity level (1-5) based on required steps and insight depth
            4. Recommend 3 distinct solution approaches with brief rationale for each
            5. Flag any potential pitfalls or common mistakes for this problem type
            Format as structured JSON with keys: domain, techniques, complexity, approaches, pitfalls""",
            context=""
        )

        # Step 2: Parallel Solution Generation
        approaches = json.loads(classification).get("approaches", [])[:3]  # Limit to 3 for efficiency
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Develop complete solution using this approach:
                {approach}
                
                Requirements:
                - Show all mathematical steps with clear justification
                - Maintain symbolic precision (no numerical approximations)
                - Verify each step against problem constraints
                - If stuck, note the obstacle and attempt alternative within same framework
                - Final answer must be an integer 000-999 if applicable""",
                context=""
            ) for approach in approaches]
        )

        # Step 3: Validation & Error Correction
        validated_solutions = []
        for attempt in solution_attempts:
            validation = await self.generate(
                instruction="""Critically validate this solution:
                1. Check logical consistency of each step
                2. Verify all mathematical operations (algebra, calculus, combinatorics)
                3. Test boundary conditions and edge cases
                4. Ensure final answer format matches requirements (integer 000-999)
                5. Identify any gaps, errors, or unjustified assumptions
                If errors found, provide specific correction instructions""",
                context=attempt
            )
            
            if "error" in validation.lower() or "gap" in validation.lower():
                corrected = await self.revise(
                    instruction=f"""Fix all identified issues:
                    Validation feedback: {validation}
                    
                    Requirements:
                    - Address every point in validation feedback
                    - Maintain original approach unless fundamentally flawed
                    - Add missing justifications or calculations
                    - Preserve correct parts of original solution
                    - Final output must be self-contained and complete""",
                    context=attempt
                )
                validated_solutions.append(corrected)
            else:
                validated_solutions.append(attempt)

        # Step 4: Hierarchical Decomposition (if complexity > 3)
        complexity = json.loads(classification).get("complexity", 3)
        if complexity > 3:
            decomposition = await self.decompose(
                instruction="""Break problem into mathematically meaningful subproblems:
                - Each subproblem should correspond to a natural mathematical step (lemma, theorem application, etc.)
                - Specify dependencies between subproblems
                - Include both computational and conceptual subproblems
                - Maximum 7 subproblems to maintain focus""",
                context=""
            )
            
            # Solve subproblems in dependency order
            solved_subproblems = {}
            for subproblem in decomposition:
                deps = subproblem.get("dependencies", "").split(",") if subproblem.get("dependencies") else []
                # Wait for dependencies (simplified - in practice would need topological sort)
                dep_context = "\n".join([solved_subproblems.get(dep.strip(), "") for dep in deps if dep.strip() in solved_subproblems])
                
                solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context from dependencies:
                    {dep_context}
                    
                    Requirements:
                    - Self-contained solution with clear reasoning
                    - Reference dependency results only as needed
                    - Verify subproblem solution independently""",
                    context=dep_context
                )
                solved_subproblems[subproblem["id"]] = solution
            
            # Integrate subproblem solutions
            integrated_solution = await self.generate(
                instruction=f"""Synthesize all subproblem solutions into final answer:
                Subproblem solutions: {json.dumps(solved_subproblems, indent=2)}
                
                Requirements:
                - Show how subproblem solutions combine
                - Verify consistency across subproblems
                - Derive final answer with complete justification
                - Format final answer as integer 000-999 if applicable""",
                context=json.dumps(solved_subproblems)
            )
            validated_solutions.append(integrated_solution)

        # Step 5: Computational Verification (if applicable)
        computational_check = await self.generate(
            instruction="""Determine if computational verification would be beneficial:
            - Problems involving sums, sequences, or large combinatorial spaces benefit from code
            - Functional equations can be tested over sample values
            - Number theory problems can be verified with modular arithmetic
            Return 'YES' if code verification recommended, 'NO' otherwise with brief rationale""",
            context=classification
        )
        
        if "YES" in computational_check.upper():
            code_verification = await self.programmer(
                instruction=f"""Generate Python code to verify or compute the solution:
                - Use exact arithmetic (fractions, integers, symbolic if needed)
                - Test multiple cases including edge cases
                - Output should be final answer or verification result
                - If computing directly, ensure precision and handle large numbers appropriately
                Problem context: {classification}""",
                context=validated_solutions[0] if validated_solutions else ""
            )
            validated_solutions.append(f"COMPUTATIONAL VERIFICATION:\n{code_verification}")

        # Step 6: Summarize & Synthesize
        solution_summaries = await asyncio.gather(
            *[self.summarize(
                instruction="""Extract key insights and final answer:
                - Condense to essential mathematical steps
                - Highlight critical insights or non-obvious transformations
                - State final answer clearly (integer 000-999 format)
                - Note any remaining uncertainties or assumptions""",
                context=sol
            ) for sol in validated_solutions]
        )

        # Step 7: Ensemble Final Answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution from all candidates:
            Selection criteria:
            1. Logical completeness and rigor
            2. Computational correctness (if verified)
            3. Elegance and insightfulness
            4. Consistency with problem constraints
            5. Clarity of final answer presentation
            
            Output format:
            - Begin with "FINAL ANSWER: [integer 000-999]"
            - Follow with concise justification (3-5 sentences)
            - End with confidence assessment (High/Medium/Low) based on verification depth""",
            contexts_list=solution_summaries
        )

        # Step 8: Confidence Report (Meta-Analysis)
        confidence_report = await self.generate(
            instruction=f"""Generate confidence report for final answer:
            Final answer: {final_answer}
            
            Analyze:
            1. Strength of mathematical reasoning
            2. Depth of verification (analytical, computational, edge cases)
            3. Consistency across multiple approaches
            4. Potential remaining weaknesses
            5. Alternative interpretations considered and rejected
            
            Format as structured report with confidence level (High/Medium/Low)""",
            context=final_answer
        )

        return f"{final_answer}\n\nCONFIDENCE REPORT:\n{confidence_report}"