# Workflow ID: mgsmbn_25_0
# Benchmark: mgsmbn
# Data Indices: [84, 37]

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

        # === PHASE 1: PARALLEL LINGUISTIC ANALYSIS ===
        entity_task = self.generate(
            instruction="""Extract all named entities and numerical quantities from the Bengali problem.
            - List each person, object, or entity mentioned.
            - Extract every number and its associated unit (টাকা, ঘণ্টা, ইঞ্চি, etc.).
            - Format as: "Entities: [list], Quantities: [list with units]".
            Focus only on explicit mentions. Do not infer relationships yet.""",
            context=""
        )
        
        relationship_task = self.generate(
            instruction="""Map all mathematical relationships and action verbs.
            - Identify comparative phrases (e.g., 'তিনগুণ বেশি' = three times more).
            - Note verbs indicating operations (e.g., 'খান' = consume, 'কাটা' = divide).
            - Flag any proportional, sequential, or distributional keywords.
            Format as: "Relationships: [list], Operations: [list], Keywords: [list]".""",
            context=""
        )
        
        constraint_task = self.generate(
            instruction="""Detect explicit and implicit constraints.
            - Physical constraints (e.g., non-negative quantities, whole people).
            - Unit consistency requirements.
            - Temporal or logical order (e.g., 'first... then...').
            - Boundary conditions (e.g., 'at least', 'no more than').
            Format as: "Constraints: [list], Units: [list], Order: [yes/no]".""",
            context=""
        )

        # Execute in parallel
        entity_analysis, relationship_analysis, constraint_analysis = await asyncio.gather(
            entity_task, relationship_task, constraint_task
        )

        # === PHASE 2: SYNTHESIZE STRUCTURED REPRESENTATION ===
        structured_context = await self.ensemble(
            instruction="""Synthesize the three analyses into a single structured representation.
            Resolve conflicts, fill gaps, and organize as:
            {
                "entities": [list from entity_analysis],
                "quantities": [list with units from entity_analysis],
                "relationships": [from relationship_analysis],
                "operations": [from relationship_analysis],
                "constraints": [from constraint_analysis],
                "target": "What final value is being asked for?"
            }
            Ensure all numerical values and their contexts are preserved. Be explicit about what needs to be calculated.""",
            contexts_list=[entity_analysis, relationship_analysis, constraint_analysis]
        )

        # === PHASE 3: PROBLEM TYPE CLASSIFICATION ===
        problem_type = await self.generate(
            instruction="""Classify this problem based on the structured context:
            - If only one mathematical operation is needed (e.g., single multiplication, addition), classify as 'Atomic'.
            - If multiple distinct steps or entities with interdependent calculations, classify as 'MultiStep'.
            Respond ONLY with 'Atomic' or 'MultiStep'. No other text.""",
            context=structured_context
        )

        # === PHASE 4: CONDITIONAL BRANCHING ===
        if "Atomic" in problem_type:
            # Direct computation for simple problems
            final_answer = await self.programmer(
                instruction=f"""Solve this atomic math problem using the structured context:
                {structured_context}
                
                Instructions:
                - Use only the values and relationships provided.
                - Handle unit conversions if needed (1 foot = 12 inches, etc.).
                - Output ONLY the numerical result. No text, no units, no explanation.
                - If ambiguous, choose the most plausible interpretation.""",
                context=structured_context
            )
        else:
            # === PHASE 5: HIERARCHICAL DECOMPOSITION ===
            subproblems = await self.decompose(
                instruction=f"""Break this multi-step problem into minimal computational subproblems.
                Use the structured context:
                {structured_context}
                
                For each subproblem:
                - Define inputs and expected output.
                - Specify dependencies (which subproblem IDs must complete first).
                - Keep each subproblem solvable with one arithmetic operation.
                Example: "Calculate Cody's cookies = 3 * Amir's cookies (5)" → depends on nothing.
                Example: "Total = Amir + Cody" → depends on subproblem 1.
                """,
                context=structured_context
            )

            # === PHASE 6: PARALLEL SUBPROBLEM EXECUTION WITH DEPENDENCIES ===
            results = {}
            # Topological sort by dependencies
            subproblem_dict = {sp['id']: sp for sp in subproblems}
            execution_order = []
            visited = set()
            
            def visit(sp_id):
                if sp_id in visited:
                    return
                visited.add(sp_id)
                deps = subproblem_dict[sp_id].get('dependencies', '').split(',') if subproblem_dict[sp_id].get('dependencies') else []
                for dep in deps:
                    dep = dep.strip()
                    if dep and dep in subproblem_dict:
                        visit(dep)
                execution_order.append(sp_id)
            
            for sp in subproblems:
                visit(sp['id'])
            
            # Execute in dependency order, parallelizing independent steps
            for sp_id in execution_order:
                sp = subproblem_dict[sp_id]
                deps = [dep.strip() for dep in sp.get('dependencies', '').split(',') if dep.strip()]
                # Wait for dependencies
                dep_context = "\n".join([f"Step {dep}: {results[dep]}" for dep in deps]) if deps else ""
                
                result = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {sp['description']}
                    
                    Context from dependencies:
                    {dep_context}
                    
                    Structured problem context:
                    {structured_context}
                    
                    Instructions:
                    - Use ONLY provided values and dependencies.
                    - Output ONLY the numerical result. No text.
                    - Convert units if needed (1 foot = 12 inches).""",
                    context=dep_context
                )
                results[sp_id] = result.strip()

            # Final answer is the last subproblem (or explicitly targetted one)
            final_subproblem_id = execution_order[-1]  # Assume last is final
            final_answer = results[final_subproblem_id]

        # === PHASE 7: VERIFICATION & FALLBACK ===
        verification = await self.revise(
            instruction=f"""Verify the final answer against the original problem and constraints.
            Final Answer: {final_answer}
            Structured Context: {structured_context}
            
            Check:
            - Does it satisfy all constraints (non-negative, unit consistency)?
            - Is it logically plausible in the real-world context?
            - Does it match the target asked for?
            If any issue, respond ONLY with 'INVALID'. Otherwise, respond 'VALID'.""",
            context=final_answer
        )

        if "INVALID" in verification:
            # Fallback: Generate verbose solution then recompute
            verbose_solution = await self.generate(
                instruction=f"""The initial solution failed verification. Generate a detailed, step-by-step solution:
                - Re-express the problem in clear mathematical terms.
                - Show all intermediate steps and assumptions.
                - Explicitly handle units and constraints.
                - Conclude with the final numerical answer.
                Format: 'Step 1: ... \nStep 2: ... \nFinal Answer: [number]'""",
                context=structured_context
            )
            
            final_answer = await self.programmer(
                instruction=f"""Extract and compute the final answer from this verbose solution:
                {verbose_solution}
                
                Output ONLY the numerical result. No text.""",
                context=verbose_solution
            )

        # Clean and return final numerical answer
        # Extract number from potential text wrapping
        match = re.search(r'[-+]?\d*\.\d+|\d+', str(final_answer))
        if match:
            return match.group(0)
        else:
            # Last resort: return as-is
            return str(final_answer).strip()