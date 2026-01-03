# Workflow ID: mgsmbn_42_0
# Benchmark: mgsmbn
# Data Indices: [135, 80]

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
        import re

        # Step 1: Extract and structure problem components with extreme specificity
        extraction_instruction = """
        Perform deep semantic extraction of the Bengali math problem. Identify:
        1. All numerical values with their exact Bengali phrases (e.g., "4টি পৃষ্ঠা" → 4)
        2. All entities (people, objects, time units) and their relationships
        3. The target unknown (what is being asked)
        4. Temporal markers (e.g., "2 বছরে" implies future state)
        5. Mathematical operations implied by context (e.g., "দ্বিগুণ" → multiplication by 2)
        6. Constraints (explicit or implicit: integer requirements, positivity, unit consistency)
        
        Format as JSON with keys: 
        - "entities": list of {"name": str, "value": number/None, "unit": str, "role": str}
        - "relationships": list of {"type": str, "operands": list, "operation": str}
        - "target": str (description of what to solve for)
        - "constraints": list of str
        - "temporal_shifts": list of {"variable": str, "shift": str, "amount": number}
        """
        structured_extraction = await self.generate(
            instruction=extraction_instruction,
            context=""
        )

        # Step 2: Decompose into mathematically executable subproblems with dependencies
        decomposition_instruction = """
        Based on the structured extraction, decompose into minimal computational steps.
        Each subproblem must:
        - Be solvable with basic arithmetic/algebra
        - Have clearly defined inputs and outputs
        - Specify dependencies on other subproblems
        - Include validation criteria (e.g., "result must be positive integer")
        
        Return list of subproblems with:
        - id: "step_1", "step_2", etc.
        - description: What to compute and how
        - dependencies: comma-separated step IDs (empty if none)
        - validation: What to check after computation
        """
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=structured_extraction
        )

        # Step 3: Generate multiple solution approaches in parallel
        async def generate_approach(approach_type):
            approach_instruction = f"""
            Solve using {approach_type} approach:
            - Algebraic: Define variables and equations
            - Arithmetic: Step-by-step calculation without variables
            - Tabular: Build table of values and interpolate
            - Guess-and-check: Iterative testing with logical bounds
            
            Use the structured extraction and subproblems as guide.
            Show ALL work. Verify against constraints.
            Return final answer as: "ANSWER: <number>"
            """
            return await self.generate(
                instruction=approach_instruction,
                context=f"Extraction: {structured_extraction}\nSubproblems: {json.dumps(subproblems)}"
            )

        approaches = await asyncio.gather(
            generate_approach("algebraic"),
            generate_approach("arithmetic"),
            generate_approach("guess-and-check")
        )

        # Step 4: Validate each approach independently
        async def validate_approach(approach_text):
            validation_instruction = """
            Critically validate this solution:
            1. Check arithmetic accuracy (recalculate key steps)
            2. Verify unit consistency (no mixing টাকা with পৃষ্ঠা)
            3. Confirm constraint satisfaction (positive, integer if required)
            4. Assess logical flow (does each step follow from previous?)
            5. Flag any assumptions not in original problem
            
            Return "VALID" if passes all checks, otherwise detailed error list.
            """
            validation = await self.generate(
                instruction=validation_instruction,
                context=approach_text
            )
            return {"solution": approach_text, "validation": validation}

        validated_approaches = await asyncio.gather(
            *[validate_approach(app) for app in approaches]
        )

        # Step 5: Ensemble - Synthesize validated solutions
        ensemble_instruction = """
        Synthesize the validated approaches:
        - If all agree, return consensus answer
        - If conflict, identify root cause (e.g., misinterpretation of "দ্বিগুণ")
        - Reconcile using original problem semantics
        - When in doubt, prefer algebraic approach for precision
        - Final answer must be single number matching "ANSWER: <number>" format
        
        Also output confidence level: HIGH (all agree), MEDIUM (2/3 agree), LOW (conflict)
        """
        ensemble_result = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=[va["solution"] for va in validated_approaches]
        )

        # Step 6: Generate executable code for highest-confidence solution
        code_instruction = """
        Generate Python code that computes the answer.
        Requirements:
        - Use only basic arithmetic and variable assignment
        - Include comments mapping each line to problem semantics
        - Validate constraints at end (assert statements)
        - Print only the final numerical answer (no text)
        
        Example:
        # Seth is twice Brooke's age: S = 2*B
        B = 8  # solved from equations
        S = 2 * B
        assert S > 0, "Age must be positive"
        print(S)
        """
        code_result = await self.programmer(
            instruction=code_instruction,
            context=f"Ensemble result: {ensemble_result}\nStructured extraction: {structured_extraction}",
            max_retries=3
        )

        # Step 7: Extract final numerical answer with fallbacks
        answer_extraction_instruction = """
        Extract the final numerical answer from any of:
        1. Code execution output (preferred)
        2. Ensemble result's "ANSWER: <number>" 
        3. Validated approaches' "ANSWER: <number>"
        
        If multiple numbers exist, select the one that appears in most sources.
        If still ambiguous, return the algebraic approach's answer.
        Output ONLY the number (integer or decimal), nothing else.
        """
        
        # Try to extract from code first
        final_answer = ""
        try:
            # Extract number from code output (last line usually)
            lines = code_result.strip().split('\n')
            for line in reversed(lines):
                if line.strip().replace('.', '').isdigit():
                    final_answer = line.strip()
                    break
        except:
            pass

        if not final_answer:
            final_answer = await self.generate(
                instruction=answer_extraction_instruction,
                context=f"Code: {code_result}\nEnsemble: {ensemble_result}\nValidated: {json.dumps(validated_approaches)}"
            )

        # Clean and return final answer
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', final_answer)
        if '.' in cleaned:
            return float(cleaned)
        else:
            return int(cleaned) if cleaned.isdigit() else cleaned