# Workflow ID: mgsmbn_107_0
# Benchmark: mgsmbn
# Data Indices: [146, 14]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # === PHASE 1: PROBLEM CLASSIFICATION & DNA EXTRACTION ===
        classification = await self.generate(
            instruction="""Thoroughly classify this Bengali math word problem by analyzing its structural and semantic DNA. Answer in this exact format:

CLASSIFICATION: [Sequential|Proportional|Temporal|Distributional|Comparative|Hybrid]
TARGET_VARIABLE: [What is being asked for? Be specific with units if mentioned]
KEY_ENTITIES: [List all named quantities, people, objects with their described values]
HIDDEN_STEPS: [Are there intermediate calculations required? Describe them]
UNIT_REQUIREMENTS: [What unit must the final answer be in? e.g., dozens, taka, hours]
CONSTRAINTS: [Any real-world constraints? e.g., no negative flowers, whole people only]

Be exhaustive. This classification will drive the entire solution strategy.""",
            context=""
        )

        # === PHASE 2: PARALLEL EXTRACTION (FORK) ===
        entity_extraction, relationship_mapping, target_analysis = await asyncio.gather(
            self.generate(
                instruction="""Extract ALL numerical entities and their direct descriptions. Format as:
ENTITY: [Name/Description] = [Value] [Unit if any]
Example: "ENTITY: White Carnations = X (unknown base)"
Include unknowns as variables. Preserve Bengali terms but add English clarification in parentheses if helpful.""",
                context=classification
            ),
            self.generate(
                instruction="""Map ALL mathematical relationships. For each, specify:
- Type: Multiplication, Division, Addition, Subtraction, Ratio, Percentage, etc.
- Operands: What two entities are related?
- Direction: Which is derived from which?
- Formula: Express as equation if possible (e.g., RedRoses = 4 × WhiteCarnations)
Be meticulous. Relationships may be embedded in phrases like 'চারগুণ' (four times).""",
                context=classification
            ),
            self.generate(
                instruction="""Analyze the target variable in depth:
- What must be calculated? 
- What knowns or intermediates are required?
- What is the expected answer format? (integer, decimal, unit)
- What common pitfalls might occur? (unit conversion, order of ops, misread multiplier)
Structure your analysis around backward-chaining: start from target and identify prerequisites.""",
                context=classification
            )
        )

        # === PHASE 3: SYNTHESIZE MATHEMATICAL MODEL ===
        model_contexts = [classification, entity_extraction, relationship_mapping, target_analysis]
        mathematical_model = await self.ensemble(
            instruction="""Synthesize all inputs into a single, executable mathematical model. Your output must include:

1. Defined Variables: List all knowns and unknowns with symbols
2. Equations: Numbered list of all governing equations derived from relationships
3. Solution Path: Step-by-step plan to solve for target variable
4. Unit Handling Plan: How units will be tracked and converted
5. Validation Checks: What real-world constraints must final answer satisfy?

This is the master plan. Be precise, structured, and complete.""",
            contexts_list=model_contexts
        )

        # === PHASE 4: SOLUTION SPIRAL (ITERATIVE REFINEMENT) ===
        current_solution = None
        for attempt in range(3):  # Max 3 refinement cycles
            if attempt == 0:
                # Initial solution generation
                current_solution = await self.generate(
                    instruction=f"""Execute the mathematical model below. Show ALL steps:

{mathematical_model}

Requirements:
- Perform calculations step by step
- Track units at every step
- Highlight intermediate results
- Box the final numerical answer at the end
- If any step is ambiguous, state your assumption explicitly""",
                    context=mathematical_model
                )
            else:
                # Validate and revise
                validation = await self.generate(
                    instruction="""Critically validate the solution below. Check for:
1. Arithmetic errors
2. Unit mismatches or missing conversions
3. Violation of real-world constraints (e.g., negative quantities)
4. Misinterpretation of relationships (e.g., confused multiplier)
5. Missing intermediate steps

If any issues found, describe them precisely. If perfect, say 'VALIDATED'.""",
                    context=current_solution
                )
                
                if "VALIDATED" in validation.upper():
                    break  # Exit loop if validated
                    
                # Revise with specific feedback
                current_solution = await self.revise(
                    instruction=f"""Revise the solution using this feedback:

{validation}

Requirements:
- Fix all identified errors
- Keep all correct steps
- Add any missing intermediate calculations
- Reaffirm unit consistency
- Re-box the final answer""",
                    context=current_solution
                )

        # === PHASE 5: ADVERSARIAL SELF-CRITIQUE (PARALLEL VALIDATION) ===
        critique_task = self.revise(
            instruction="""Adversarial Critique Mode: Assume this solution is WRONG. 
Your job is to find the MOST LIKELY error. Consider:
- Did they misread 'চারগুণ' as addition instead of multiplication?
- Did they forget to convert units (e.g., eggs to dozens)?
- Did they solve for wrong variable?
- Did they ignore a constraint (e.g., time limit, whole numbers)?
- Is the final answer implausible in real-world context?

If you find a credible error, describe it and how to fix. If no error, say 'NO PLAUSIBLE ERROR FOUND'.""",
            context=current_solution
        )

        unit_sanitize_task = self.generate(
            instruction="""Extract ONLY the final numerical answer from the solution below. 
Rules:
- Remove all text, units, explanations
- If answer is in wrong unit, convert it (e.g., 84 eggs → 7 dozens)
- Round to integer if problem implies whole units (people, flowers)
- Return ONLY the number, nothing else
- If multiple numbers, pick the one that answers the question""",
            context=current_solution
        )

        # Run critique and sanitization in parallel
        critique_result, sanitized_answer = await asyncio.gather(critique_task, unit_sanitize_task)

        # If critique found error, attempt one final revision
        if "NO PLAUSIBLE ERROR FOUND" not in critique_result.upper():
            current_solution = await self.revise(
                instruction=f"""Final emergency revision based on adversarial critique:

{critique_result}

Fix the most critical error identified. Preserve correct parts. Re-calculate only what's necessary. Re-box final answer.""",
                context=current_solution
            )
            
            # Re-sanitize after revision
            sanitized_answer = await self.generate(
                instruction="""Extract ONLY the final numerical answer... [same as above]""",
                context=current_solution
            )

        # === PHASE 6: FINAL OUTPUT EXTRACTION ===
        # Clean the answer - extract first number from string
        match = re.search(r'[-+]?\d*\.\d+|\d+', sanitized_answer)
        final_answer = match.group(0) if match else "0"

        # Ensure integer if no decimal in problem (heuristic)
        if '.' not in final_answer and 'দশমিক' not in self.problem_text and 'ভগ্নাংশ' not in self.problem_text:
            final_answer = str(int(float(final_answer)))

        return final_answer