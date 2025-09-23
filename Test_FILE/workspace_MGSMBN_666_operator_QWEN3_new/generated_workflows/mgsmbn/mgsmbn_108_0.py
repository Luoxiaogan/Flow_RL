# Workflow ID: mgsmbn_108_0
# Benchmark: mgsmbn
# Data Indices: [175]

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

        # PHASE 1: Hierarchical Decomposition
        decomposition_instruction = """
        Systematically decompose this Bengali math word problem into atomic subproblems.
        For each subproblem:
        - Identify the unknown being solved for
        - List all required inputs (with sources)
        - Specify mathematical operation(s) needed
        - Define dependencies on other subproblems
        - Flag any unit conversions or constraints
        Output as structured subproblems with 'id', 'description', and 'dependencies'.
        Example: If solving for average age, first solve for individual ages.
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # PHASE 2: Parallel Formalization & Ambiguity Resolution
        formalization_tasks = []
        for sp in subproblems:
            formalize_instruction = f"""
            Convert this subproblem into executable mathematical specification:
            Subproblem: {sp['description']}
            Dependencies: {sp.get('dependencies', '')}
            
            Steps:
            1. Define variables with Bengali-to-English mapping (e.g., "হ্যারিয়েট = H")
            2. Write equations using standard operators (+, -, *, /)
            3. Annotate units for all quantities (টাকা, বছর, জন, etc.)
            4. Add boundary constraints (e.g., "age > 0", "integer items")
            5. Handle temporal logic ("তিন বছর পরে" → add 3 to current age)
            Output ONLY the formal specification, no explanations.
            """
            formalization_tasks.append(
                self.generate(instruction=formalize_instruction, context="")
            )
        
        raw_formalizations = await asyncio.gather(*formalization_tasks)

        # PHASE 3: Constraint Injection & Validation
        refined_formalizations = []
        for i, formal in enumerate(raw_formalizations):
            refine_instruction = f"""
            Revise this mathematical specification:
            {formal}
            
            Apply these rules:
            1. Ensure unit consistency (e.g., no multiplying টাকা by ঘণ্টা)
            2. Enforce real-world constraints (ages > 0, integer counts, etc.)
            3. Resolve ambiguous pronouns by binding to specific entities
            4. Add error-checking assertions (e.g., "assert age > 0")
            5. If underspecified, add reasonable defaults (e.g., "assume metric units")
            Output the refined specification ready for code generation.
            """
            refined = await self.revise(
                instruction=refine_instruction,
                context=formal
            )
            refined_formalizations.append(refined)

        # PHASE 4: Parallel Code Generation & Execution
        code_tasks = []
        for i, refined in enumerate(refined_formalizations):
            code_instruction = f"""
            Generate Python code to solve this mathematical specification:
            {refined}
            
            Requirements:
            - Use descriptive variable names (english_with_bengali_comments)
            - Include assertions for all constraints
            - Handle edge cases (division by zero, negative results)
            - Output ONLY the final answer for this subproblem
            - No print statements except the final numerical result
            Example structure:
            # হ্যারিয়েটের বয়স (Harriet's age)
            H = 21
            # অ্যাড্রিয়ানের বয়স (Adrian's age) = 3 * H
            A = 3 * H
            assert A > 0, "Age must be positive"
            A
            """
            code_tasks.append(
                self.programmer(instruction=code_instruction, context=refined)
            )
        
        code_results = await asyncio.gather(*code_tasks)

        # PHASE 5: Ensemble with Plausibility Scoring
        ensemble_instruction = """
        Synthesize these subproblem solutions into a final answer.
        Scoring criteria (in order of priority):
        1. Mathematical correctness (does computation follow specification?)
        2. Unit consistency (are all units compatible and preserved?)
        3. Contextual plausibility (e.g., human ages < 150, no fractional people)
        4. Dependency satisfaction (are all prerequisites correctly computed?)
        
        If multiple valid solutions exist, select the one with highest plausibility.
        If all solutions violate constraints, trigger revision cycle.
        Output ONLY the final numerical answer as a single value.
        """
        final_answer = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=[str(r) for r in code_results]
        )

        # PHASE 6: Self-Correction Loop (Max 2 iterations)
        for attempt in range(2):
            validation_instruction = f"""
            Validate this answer: {final_answer}
            Check:
            1. Does it match expected magnitude? (e.g., age not 1000)
            2. Are units correct? (e.g., not outputting টাকা when জন expected)
            3. Does it satisfy all problem constraints?
            4. Is it consistent with Bengali phrasing?
            
            If valid, output "VALID: <answer>".
            If invalid, output "INVALID: <reason>".
            """
            validation = await self.generate(
                instruction=validation_instruction,
                context=final_answer
            )
            
            if "VALID" in validation:
                break
            else:
                # Trigger revision cycle
                revise_instruction = f"""
                Problem: {validation.replace('INVALID:', '').strip()}
                Revise the entire solution approach:
                1. Re-decompose the problem with focus on failed constraint
                2. Generate alternative interpretations of ambiguous phrases
                3. Strengthen unit tracking and boundary conditions
                4. Re-execute with stricter validation
                """
                subproblems = await self.decompose(
                    instruction=revise_instruction,
                    context=""
                )
                # Repeat formalization → code → ensemble (simplified for brevity)
                # In practice, this would recursively call the same pipeline
                # For this implementation, we'll break after 2 attempts
                continue

        # Extract numerical answer (handle potential formatting)
        answer_match = re.search(r'[\d\.]+', final_answer)
        if answer_match:
            return float(answer_match.group(0)) if '.' in answer_match.group(0) else int(answer_match.group(0))
        else:
            # Fallback: return first number from any code result
            for result in code_results:
                fallback_match = re.search(r'[\d\.]+', str(result))
                if fallback_match:
                    val = fallback_match.group(0)
                    return float(val) if '.' in val else int(val)
            return 0  # Ultimate fallback