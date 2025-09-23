# Workflow ID: mgsmbn_117_0
# Benchmark: mgsmbn
# Data Indices: [119, 169]

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

        # STEP 1: STRUCTURAL DECOMPOSITION
        # Extract all entities, quantities, relationships, and unknowns with explicit referents
        decomposition = await self.generate(
            instruction="""Perform a complete structural decomposition of this Bengali math word problem. Identify:

1. ENTITIES: List every distinct object, person, or group mentioned (e.g., "লাল মুরগি", "প্রথম বক্স"). For each, note its role.

2. QUANTITIES: Extract every number or fraction, whether written as digits or Bengali words. For each, specify:
   - The exact value
   - What entity it describes
   - Its unit (টাকা, টি, ঘণ্টা, etc.) if any
   - Whether it's given or unknown

3. RELATIONSHIPS: Map all comparative or operational relationships. For each, specify:
   - The operation (addition, multiplication, fraction, etc.)
   - The source entity/quantity
   - The target entity/quantity
   - Any conditions or constraints

4. UNKNOWN: Clearly state what the problem is asking you to find.

5. AMBIGUITIES: Flag any phrases where referents are unclear (e.g., "that box" — which one?) or operations are ambiguous.

Format your output as a structured markdown list with clear section headers. Be meticulous — missing a single relationship can derail the entire solution.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION
        # Generate three independent solution approaches
        strategy_tasks = [
            self.generate(
                instruction=f"""Solve the problem using a CHRONOLOGICAL/PROCEDURAL approach:

Given the decomposition:
{decomposition}

- Model the problem as a sequence of events or steps in the order they occur or should be calculated.
- Show each intermediate calculation explicitly.
- Track units throughout.
- Assume real-world constraints (no negative counts, whole chickens, etc.).
- If any step is ambiguous, state your assumption clearly.
- End with the final numerical answer.

Show your work step by step. Do not skip arithmetic.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve the problem using an ALGEBRAIC/EQUATIONAL approach:

Given the decomposition:
{decomposition}

- Assign variables to unknown quantities.
- Write equations based on the relationships identified.
- Solve the system step by step, showing algebraic manipulation.
- Substitute known values early or late? Justify your choice.
- Verify that the solution satisfies all constraints.
- End with the final numerical answer.

Show every equation and substitution. Do not skip steps.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve the problem using a UNIT/PROPORTIONAL approach:

Given the decomposition:
{decomposition}

- Focus on ratios, proportions, scaling factors, and unit consistency.
- Express all quantities in comparable units.
- Use dimensional analysis where applicable.
- Check that proportional relationships are applied to the correct base quantities.
- Highlight any scaling factors or conversion multipliers.
- End with the final numerical answer.

Show how units propagate through calculations. Justify each proportional step.""",
                context=decomposition
            )
        ]

        strategy_results = await asyncio.gather(*strategy_tasks)

        # STEP 3: ENSEMBLE WITH CONFLICT DETECTION
        # Synthesize the three strategies, flagging disagreements
        synthesis = await self.ensemble(
            instruction="""You are given three independent solution attempts for the same Bengali math problem. Your task:

1. COMPARE all three solutions:
   - Do they arrive at the same final numerical answer?
   - If not, where do they diverge? (Which step? Which assumption?)

2. ANALYZE the point of divergence:
   - Which solution's interpretation of the problem decomposition is most faithful?
   - Which approach handles units and constraints most rigorously?

3. SYNTHESIZE a unified solution:
   - If all agree, adopt the answer and note consensus.
   - If two agree and one differs, adopt the majority and explain why the outlier is wrong.
   - If all differ, identify the most plausible answer based on decomposition fidelity and real-world constraints.

4. OUTPUT:
   - The final agreed-upon numerical answer
   - A brief justification (1-2 sentences) for why this answer is correct
   - Any remaining uncertainties or assumptions made

Format: "ANSWER: [number] | JUSTIFICATION: [text]" """,
            contexts_list=strategy_results
        )

        # STEP 4: META-VALIDATION LOOP (up to 2 iterations)
        validated = False
        current_solution = synthesis
        for _ in range(2):  # Max 2 revision cycles
            validation = await self.generate(
                instruction=f"""Act as a META-VALIDATOR. Critique this solution:

{current_solution}

Check:
1. Does the final answer make sense in the real-world context? (e.g., no fractional chickens, positive counts, plausible magnitudes)
2. Are all intermediate steps consistent with the original problem's relationships?
3. Were any ambiguities in the decomposition resolved correctly?
4. Is the unit handling consistent throughout?

If VALID: Output "VALID: [answer]"
If INVALID: Output "INVALID: [specific reason]" and suggest which part needs revision.

Be brutally honest. If in doubt, mark invalid.""",
                context=current_solution
            )

            if "VALID:" in validation:
                validated = True
                break
            else:
                # Revise the synthesis based on validation feedback
                current_solution = await self.revise(
                    instruction=f"""Revise the solution based on this validation critique:

{validation}

Specifically:
- Correct the identified error or ambiguity
- Re-check the step that was flagged
- Maintain the structure of the synthesis output format
- Do not change correct parts

Output in the same "ANSWER: | JUSTIFICATION:" format.""",
                    context=current_solution
                )

        # STEP 5: FINAL ANSWER EXTRACTION
        # Strip away all reasoning, output only the number
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the text below. 

Rules:
- Remove all units, labels, justifications, and punctuation
- If the answer is in a sentence, extract only the number
- If multiple numbers, pick the one that is the final answer
- Output must be a single integer or decimal number
- Do not add any text, explanation, or formatting

Example outputs: "42", "3.14", "1250" """,
            context=current_solution
        )

        # Clean the answer (remove commas, spaces, etc.)
        clean_answer = re.sub(r'[^\d.]', '', final_answer.strip())
        
        return clean_answer