# Workflow ID: mgsmbn_106_0
# Benchmark: mgsmbn
# Data Indices: [136, 143]

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

        # PHASE 1: SEMANTIC FRAMING — Extract entities, relationships, and implicit operations
        semantic_frame = await self.generate(
            instruction="""Perform deep semantic analysis of this Bengali math problem. Extract:
            1. All named entities (people, groups, objects) and their associated quantities.
            2. All numerical values and their contextual meaning (e.g., '80 জন জাপানিজ' → 80 people, Japanese).
            3. All relational phrases (e.g., 'দ্বিগুণের থেকে বেশি' → multiply by 2 then add) and map them to mathematical operations.
            4. The final unknown being asked for.
            5. Any constraints (non-negative, integer-only, unit consistency).
            Output in structured JSON-like format with keys: entities, values, operations, target, constraints.""",
            context=""
        )

        # PHASE 2: STRUCTURAL DECOMPOSITION — Break into atomic, ordered subproblems
        subproblems = await self.decompose(
            instruction=f"""Using the semantic frame:
            {semantic_frame}
            
            Decompose the problem into minimal, atomic subproblems. Each subproblem must:
            - Require only one mathematical operation (add, subtract, multiply, divide, compare)
            - Have clearly defined inputs (from problem or previous subproblems)
            - Specify expected output and unit
            - Be ordered by dependency (earlier IDs must be solvable first)
            Return as list of dicts with keys: id, description, dependencies (comma-separated IDs), operation, inputs, unit.""",
            context=semantic_frame
        )

        # If no decomposition (simple problem), solve directly
        if len(subproblems) == 0 or (len(subproblems) == 1 and not subproblems[0].get('dependencies')):
            # Simple case: solve with programmer + generate ensemble
            direct_solutions = await asyncio.gather(
                self.generate(
                    instruction="Solve the problem step by step in Bengali, then output only the final numerical answer.",
                    context=""
                ),
                self.programmer(
                    instruction="Write Python code to compute the answer. Return only the numerical result.",
                    context=semantic_frame,
                    max_retries=2
                )
            )
            
            final_answer = await self.ensemble(
                instruction="""You have two solutions to the same problem. 
                Compare them for numerical equivalence and contextual appropriateness (units, constraints like non-negative integers).
                If they agree, return the number. If they disagree, choose the one that respects problem constraints and explain why.
                Output ONLY the final numerical value, nothing else.""",
                contexts_list=direct_solutions
            )
            return final_answer.strip()

        # PHASE 3: PARALLEL SUBPROBLEM SOLVING — Dual-modality (Generate + Programmer) for each subproblem
        solved_subproblems = {}
        
        for sub in subproblems:
            sub_id = sub['id']
            sub_desc = sub['description']
            dependencies = sub.get('dependencies', "").split(',') if sub.get('dependencies') else []
            
            # Wait for dependencies (naive but safe for small graphs)
            for dep in dependencies:
                if dep.strip() and dep.strip() not in solved_subproblems:
                    # In practice, we'd topologically sort, but for grade-school problems, linear order suffices
                    pass
            
            # Solve subproblem with two methods in parallel
            linguistic_solution = await self.generate(
                instruction=f"""Subproblem: {sub_desc}
                Solve this using step-by-step reasoning in Bengali. Focus on the exact operation and inputs.
                Output ONLY the numerical result, nothing else.""",
                context=semantic_frame
            )
            
            programmatic_solution = await self.programmer(
                instruction=f"""Subproblem: {sub_desc}
                Inputs: {sub.get('inputs', 'from context')}
                Operation: {sub.get('operation', 'infer')}
                Write a Python function that computes this. Return only the numerical result.
                Handle units and constraints: {sub.get('unit', 'none')}, {semantic_frame}""",
                context=semantic_frame,
                max_retries=2
            )
            
            # Ensemble to reconcile
            reconciled = await self.ensemble(
                instruction=f"""Subproblem: {sub_desc}
                You have two solutions:
                A (Linguistic): {linguistic_solution}
                B (Programmatic): {programmatic_solution}
                
                Compare them. If numerically equal, return the value.
                If different, choose based on: unit consistency, problem constraints (e.g., no fractional people), and mathematical correctness.
                Output ONLY the final numerical value for this subproblem.""",
                contexts_list=[linguistic_solution, programmatic_solution]
            )
            
            solved_subproblems[sub_id] = {
                'description': sub_desc,
                'value': reconciled.strip(),
                'unit': sub.get('unit', '')
            }

        # PHASE 4: SYNTHESIZE FINAL ANSWER — Chain subproblem results
        synthesis_context = "\n".join([
            f"Step {sub_id}: {data['description']} → {data['value']} {data['unit']}"
            for sub_id, data in solved_subproblems.items()
        ])
        
        final_computation = await self.generate(
            instruction=f"""Using these solved subproblems:
            {synthesis_context}
            
            Combine them in the correct order to compute the final answer to the original question.
            Show the full formula or reasoning chain, then output ONLY the final numerical answer.
            Respect all constraints from semantic frame: {semantic_frame}""",
            context=synthesis_context
        )

        # PHASE 5: VALIDATION LOOP — Up to 2 retries for sanity check
        answer = final_computation
        for _ in range(2):
            validation = await self.revise(
                instruction=f"""Validate this answer: {answer}
                Check against original problem constraints:
                - Units must match (টাকা, জন, etc.)
                - No negative counts or fractional people unless explicitly allowed
                - Arithmetic must be consistent with subproblem chain
                If valid, return "VALID: <answer>". If invalid, return "INVALID" and the corrected calculation.""",
                context=semantic_frame + "\n" + synthesis_context
            )
            
            if "VALID:" in validation:
                answer = validation.split("VALID:")[-1].strip()
                break
            else:
                # Attempt correction
                answer = await self.generate(
                    instruction=f"""Correct the answer based on validation feedback:
                    Validation: {validation}
                    Previous answer: {answer}
                    Subproblems: {synthesis_context}
                    Output ONLY the corrected numerical value.""",
                    context=validation
                )

        return answer.strip()