# Workflow ID: mgsmbn_113_0
# Benchmark: mgsmbn
# Data Indices: [79, 171]

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

        # Step 1: Classify problem type and complexity
        classification = await self.generate(
            instruction="""Thoroughly analyze the Bengali word problem and classify it with extreme precision. Output in this exact format:

PROBLEM_TYPE: [sequential|proportional|rate|distribution|comparison|multi_entity|other]
COMPLEXITY: [low|medium|high]
KEY_ENTITIES: List all named entities (people, objects) and their initial numerical values
RELATIONSHIPS: List all mathematical relationships between entities (e.g., 'A = B + 10', 'C = 0.25 * D')
EXPECTED_ANSWER_TYPE: [integer|decimal]
UNITS: [টাকা|ঘণ্টা|জিনিস|বার|জন|other]
HIDDEN_CONSTRAINTS: Any implicit real-world constraints (e.g., 'must be positive', 'must be integer')

Be exhaustive. If any field is uncertain, state 'UNKNOWN' rather than guessing.""",
            context=""
        )

        # Step 2: Parallel extraction - entities and relationships
        entity_extraction, relationship_extraction = await asyncio.gather(
            self.generate(
                instruction="""Extract ALL numerical values and their semantic context from the problem. For each number, specify:
- What entity or quantity it represents
- Its role in the problem (initial value, target, intermediate)
- Any direct modifiers (e.g., 'more than', 'less than', 'times')

Format as bullet points. Be literal and precise.""",
                context=""
            ),
            self.generate(
                instruction="""Extract ALL logical and mathematical relationships between quantities. Include:
- Explicit equations (A = B + 5)
- Comparative relationships (A is twice B)
- Sequential dependencies (first, then, finally)
- Conditional statements (if, when)

Translate Bengali relational phrases into mathematical notation. Preserve original wording in parentheses for reference.""",
                context=""
            )
        )

        # Step 3: Build unified problem model
        problem_model = await self.generate(
            instruction=f"""Synthesize the following extractions into a unified, structured problem model:

CLASSIFICATION:
{classification}

ENTITY EXTRACTION:
{entity_extraction}

RELATIONSHIP EXTRACTION:
{relationship_extraction}

Create a comprehensive model that includes:
1. A dictionary of known values
2. A list of equations/relationships in solvable order
3. Identification of the target unknown
4. Any missing information that must be inferred

Format as clear, labeled sections. This model will drive all subsequent calculations.""",
            context=f"{classification}\n\n{entity_extraction}\n\n{relationship_extraction}"
        )

        # Step 4: Conditional branching based on complexity
        if "COMPLEXITY: low" in classification:
            # Direct solution path
            direct_solution = await self.programmer(
                instruction=f"""Using the problem model below, write Python code to compute the answer.
- Define variables clearly
- Show all steps
- Output only the final numerical answer

Problem Model:
{problem_model}""",
                context=problem_model
            )
            final_answer = direct_solution
        else:
            # Decomposition path
            subproblems = await self.decompose(
                instruction=f"""Break this problem into minimal, sequentially dependent subproblems based on the problem model. Each subproblem must:
- Be solvable with information available at that step
- Have clear input and output
- Specify dependencies by ID
- Represent exactly one calculation or inference

Problem Model:
{problem_model}

Output as list of dictionaries with keys: id, description, dependencies""",
                context=problem_model
            )

            # Solve each subproblem with dual-path verification
            subproblem_solutions = {}
            subproblem_ids = [sp['id'] for sp in subproblems]
            
            for sp in subproblems:
                # Get dependencies
                deps = sp['dependencies'].split(',') if sp['dependencies'] else []
                dep_context = "\n".join([f"Subproblem {dep}: {subproblem_solutions.get(dep, 'UNKNOWN')}" for dep in deps])
                
                # Dual-path solving
                narrative_solution = await self.generate(
                    instruction=f"""Solve subproblem: {sp['description']}
Using these dependencies:
{dep_context}

Show step-by-step reasoning. Justify each operation. Output only the final value with unit if applicable.""",
                    context=dep_context
                )
                
                code_solution = await self.programmer(
                    instruction=f"""Write Python code to solve: {sp['description']}
Dependencies context:
{dep_context}

Define variables clearly. Output only the numerical result.""",
                    context=dep_context
                )
                
                # Ensemble to verify
                verified_solution = await self.ensemble(
                    instruction=f"""Compare these two solutions for subproblem {sp['id']}: 
NARRATIVE: {narrative_solution}
CODE: {code_solution}

If they agree, output the value. If they disagree, identify the error and output the corrected value. Output ONLY the final numerical value.""",
                    contexts_list=[narrative_solution, code_solution]
                )
                
                subproblem_solutions[sp['id']] = verified_solution

            # Final synthesis
            all_solutions_context = "\n".join([f"{id}: {sol}" for id, sol in subproblem_solutions.items()])
            final_answer = await self.generate(
                instruction=f"""Synthesize the subproblem solutions into the final answer:
{all_solutions_context}

The target is: {problem_model}

Output ONLY the final numerical answer, nothing else.""",
                context=all_solutions_context
            )

        # Step 5: Validation and sanity check
        validation = await self.generate(
            instruction=f"""Validate the answer: {final_answer}
Against original problem: {self.problem_text}

Check:
1. Does it satisfy all stated conditions?
2. Is it in the expected unit and format?
3. Is it within plausible real-world bounds?
4. Does it match implicit constraints?

If valid, output "VALID: [answer]". If invalid, output "INVALID: [correction]".""",
            context=final_answer
        )

        if "INVALID" in validation:
            # One repair attempt
            final_answer = await self.revise(
                instruction=f"""Correct the answer based on validation feedback:
{validation}

Original problem: {self.problem_text}
Previous answer: {final_answer}

Output only the corrected numerical value.""",
                context=final_answer
            )

        # Step 6: Final ensemble for robustness (generate 3 answers, take consensus)
        direct_answer = await self.programmer(
            instruction="Solve the original problem directly with Python code. Output only the numerical answer.",
            context=""
        )
        
        narrative_answer = await self.generate(
            instruction="Solve the problem with step-by-step reasoning. Output only the final numerical answer.",
            context=""
        )
        
        final_ensemble = await self.ensemble(
            instruction=f"""Three candidate answers:
1. Decomposed path: {final_answer}
2. Direct code: {direct_answer}
3. Narrative reasoning: {narrative_answer}

Select the answer that appears in at least two solutions. If all differ, choose the one that best satisfies problem constraints. Output ONLY the numerical value.""",
            contexts_list=[final_answer, direct_answer, narrative_answer]
        )

        return final_ensemble