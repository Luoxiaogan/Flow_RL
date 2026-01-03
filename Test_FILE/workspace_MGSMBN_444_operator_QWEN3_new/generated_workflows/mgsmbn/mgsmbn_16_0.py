# Workflow ID: mgsmbn_16_0
# Benchmark: mgsmbn
# Data Indices: [69, 74]

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

        # PHASE 1: PARALLEL INTERPRETATION (Diamond Pattern - Fork)
        linguistic_analysis = await self.generate(
            instruction="""Perform deep linguistic deconstruction of the Bengali problem:
            - Identify all named entities (people, objects, groups) and their roles
            - Extract every numerical value and its associated unit (টাকা, পাউন্ড, জন, etc.)
            - Map action verbs to mathematical operations (e.g., 'খাবে' → consumption → subtraction from total)
            - Flag ambiguous phrases or potential misinterpretations
            - Note cultural or contextual assumptions (e.g., 'পিকনিক' implies shared food distribution)
            Output as structured bullet points with categories: Entities, Quantities, Actions, Ambiguities, Assumptions.""",
            context=""
        )

        mathematical_modeling = await self.generate(
            instruction="""Construct a formal mathematical model:
            - Define variables for unknowns
            - Write equations representing relationships (ratios, proportions, sequences)
            - Identify type of problem: distribution, rate, comparison, etc.
            - Specify required operations and their order
            - Highlight any hidden steps or intermediate calculations needed
            Format as: Variables: {...}, Equations: [...], Operations: [...], Notes: [...]""",
            context=""
        )

        contextual_reasoning = await self.generate(
            instruction="""Apply real-world reasoning and constraint validation:
            - What physical/logical constraints apply? (e.g., no negative people, fractional dinosaurs?)
            - Are units consistent? If not, what conversions are needed?
            - Does the scenario imply unstated constraints? (e.g., 'পর্যাপ্ত পরিমাণ' implies no leftovers or shortages)
            - What edge cases might break the model?
            Output as: Constraints: [...], Unit Analysis: [...], Edge Cases: [...], Validation Rules: [...]""",
            context=""
        )

        # PHASE 2: CRITIQUE & REFINEMENT (Adversarial Validation)
        refined_linguistic = await self.revise(
            instruction=f"""Critique and refine the linguistic analysis:
            - Resolve ambiguities flagged in original analysis
            - Cross-validate entity roles with mathematical model
            - Ensure no quantity is misattributed
            - Strengthen cultural/contextual assumptions with evidence from text
            - Output must be unambiguous and mathematically actionable""",
            context=linguistic_analysis
        )

        refined_mathematical = await self.revise(
            instruction=f"""Critique and refine the mathematical model:
            - Verify equations match linguistic relationships
            - Check operation order against chronological or logical sequence in problem
            - Ensure all variables are defined and solvable
            - Add missing steps if any
            - Confirm model handles edge cases identified in contextual reasoning""",
            context=mathematical_modeling
        )

        refined_contextual = await self.revise(
            instruction=f"""Strengthen constraint validation:
            - Make constraints explicit and quantifiable
            - Add unit conversion rules if needed
            - Formalize validation rules as boolean checks
            - Ensure no contradiction with linguistic or mathematical models""",
            context=contextual_reasoning
        )

        # PHASE 3: SYNTHESIZE UNIFIED MODEL (Ensemble Merge)
        unified_model = await self.ensemble(
            instruction="""Synthesize the three refined analyses into one coherent problem model:
            - Integrate entities, equations, and constraints
            - Resolve any conflicts between perspectives
            - Produce a single, executable mathematical plan
            - Include all necessary steps in logical order
            - Format as: PLAN: [numbered steps], VALIDATION: [pre-check rules], OUTPUT: [expected format]""",
            contexts_list=[refined_linguistic, refined_mathematical, refined_contextual]
        )

        # PHASE 4: PARALLEL SOLUTION GENERATION (Dual-path Redundancy)
        algebraic_solution = await self.generate(
            instruction=f"""Solve using algebraic formalism:
            - Use variables and equations from unified model
            - Show all symbolic manipulations
            - Substitute values only at final step
            - Box final answer
            - Verify against validation rules""",
            context=unified_model
        )

        arithmetic_solution = await self.generate(
            instruction=f"""Solve using step-by-step arithmetic:
            - Break into discrete calculation steps
            - Show intermediate values with units
            - Explain each operation in context of problem
            - Verify each step against constraints
            - Box final answer""",
            context=unified_model
        )

        # PHASE 5: CROSS-VALIDATION & ARBITRATION
        validation_report = await self.generate(
            instruction=f"""Compare algebraic and arithmetic solutions:
            - Do they agree numerically?
            - If not, identify source of discrepancy
            - Check which solution better satisfies validation rules
            - Recommend final answer or trigger arbitration
            Output: AGREEMENT: [yes/no], DISCREPANCY: [description if any], RECOMMENDATION: [answer or 'arbitrate']""",
            context=f"Algebraic: {algebraic_solution}

Arithmetic: {arithmetic_solution}"
        )

        if "arbitrate" in validation_report.lower() or "disagreement" in validation_report.lower():
            arbitrated_solution = await self.ensemble(
                instruction="""Act as arbiter:
                - Analyze both solutions and validation report
                - Identify which approach made fewer assumptions
                - Select solution that best satisfies constraints and linguistic fidelity
                - If still uncertain, create hybrid solution
                - Output ONLY the final numerical answer in boxed format""",
                contexts_list=[algebraic_solution, arithmetic_solution, validation_report]
            )
            final_answer_text = arbitrated_solution
        else:
            final_answer_text = algebraic_solution if "algebraic" in validation_report.lower() else arithmetic_solution

        # PHASE 6: META-COGNITIVE CONFIDENCE CHECK (Iterative Refinement)
        confidence_analysis = await self.generate(
            instruction=f"""Self-assess confidence in final answer:
            - Rate confidence 1-10 based on: clarity of problem, consistency of models, validation strength
            - List any remaining uncertainties
            - If confidence < 8, suggest specific improvements
            Output: CONFIDENCE: [score], UNCERTAINTIES: [...], SUGGESTIONS: [...]""",
            context=final_answer_text
        )

        if "confidence: [1-7]" in confidence_analysis.lower() or "uncertainties" in confidence_analysis.lower():
            # One refinement loop
            refined_final = await self.revise(
                instruction=f"""Improve solution based on confidence analysis:
                - Address specific uncertainties raised
                - Strengthen weak assumptions
                - Recalculate if necessary
                - Maintain boxed final answer format""",
                context=final_answer_text
            )
            final_answer_text = refined_final

        # PHASE 7: ANSWER EXTRACTION & FORMATTING
        extracted_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer:
            - Ignore all reasoning, steps, and units
            - If multiple numbers, select the one that answers the question
            - Must be a single integer or decimal
            - Remove any text, brackets, or formatting
            Example output: 225""",
            context=final_answer_text
        )

        # Clean and return
        clean_answer = re.sub(r'[^\d\.]', '', extracted_answer.strip())
        return clean_answer