# Workflow ID: mgsmbn_39_0
# Benchmark: mgsmbn
# Data Indices: [4]

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
        import json

        # PHASE 1: PARALLEL DECOMPOSITION - Launch three analytical lenses simultaneously
        linguistic_analysis, mathematical_modeling, contextual_framing = await asyncio.gather(
            self.generate(
                instruction="""Perform deep linguistic decomposition of the Bengali problem text. Extract:
                1. All named entities (people, objects, places) with their roles
                2. All numerical values with their associated units and contextual meaning
                3. Temporal or conditional modifiers (e.g., 'প্রতি দ্বিতীয়', 'পরে', 'মোট')
                4. Implicit constraints (e.g., non-negative, integer-only, real-world plausibility)
                5. Action verbs indicating mathematical operations (কিনলেন → purchase → addition of cost)
                
                Format as structured JSON with keys: entities, values, modifiers, constraints, operations.
                Be exhaustive — even seemingly minor phrases may encode critical mathematical relationships.""",
                context=""
            ),
            self.generate(
                instruction="""Attempt pure mathematical modeling without full linguistic parsing. Treat the problem as a symbolic puzzle:
                1. Identify all numbers and their potential mathematical roles (constants, variables, coefficients)
                2. Infer operations from context (sequencing implies addition/subtraction, rates imply multiplication/division)
                3. Construct step-by-step calculation pathways
                4. Propose at least two different solution approaches if ambiguity exists
                5. Flag any dimensional inconsistencies or unit mismatches
                
                Present as: "Approach 1: [steps] → Result: X. Approach 2: [steps] → Result: Y. Confidence: High/Medium/Low".""",
                context=""
            ),
            self.generate(
                instruction="""Classify and contextualize the problem:
                1. Problem type: Sequential, Rate, Proportional, Distribution, Comparison, Multi-entity
                2. Real-world domain: Finance, Distance/Time, Inventory, Population, etc.
                3. Expected answer constraints: Must be integer? Positive? Within specific range?
                4. Common pitfalls for this problem type (e.g., order of operations, hidden steps)
                5. Plausibility check: What would make an answer obviously wrong?
                
                Format as bullet-point analysis with clear headers for each category.""",
                context=""
            )
        )

        # PHASE 2: CROSS-REVISION - Each analysis revises the others
        refined_linguistic = await self.revise(
            instruction=f"""Incorporate insights from mathematical modeling and contextual framing:
            Mathematical Insights: {mathematical_modeling}
            Contextual Insights: {contextual_framing}
            
            Revise your linguistic decomposition to:
            - Resolve any ambiguities using mathematical structure
            - Apply contextual constraints to filter implausible interpretations
            - Explicitly map linguistic phrases to mathematical operations
            - Highlight any remaining uncertainties that could affect the solution""",
            context=linguistic_analysis
        )

        refined_mathematical = await self.revise(
            instruction=f"""Incorporate insights from linguistic decomposition and contextual framing:
            Linguistic Insights: {refined_linguistic}
            Contextual Insights: {contextual_framing}
            
            Revise your mathematical model to:
            - Use entity names and units from linguistic analysis for clarity
            - Apply contextual constraints (e.g., round to integer, enforce positivity)
            - Resolve ambiguities using linguistic modifiers (e.g., 'প্রতি দ্বিতীয়' → alternating pattern)
            - Present final calculation with explicit unit tracking and step justification""",
            context=mathematical_modeling
        )

        refined_contextual = await self.revise(
            instruction=f"""Incorporate insights from linguistic and mathematical analyses:
            Linguistic Insights: {refined_linguistic}
            Mathematical Insights: {refined_mathematical}
            
            Refine your contextual framing to:
            - Validate that mathematical solution satisfies real-world constraints
            - Identify any edge cases not covered by current solution
            - Suggest plausibility bounds for final answer
            - Flag any remaining risks or assumptions""",
            context=contextual_framing
        )

        # PHASE 3: ENSEMBLE SYNTHESIS - Build unified solution narrative
        unified_solution = await self.ensemble(
            instruction="""Synthesize the three revised analyses into a single, coherent solution:
            1. Start with problem restatement in clear Bengali/mathematical hybrid
            2. Present step-by-step calculation with explicit justification for each step
            3. Track units throughout (টাকা, ঘণ্টা, জিনিস, etc.)
            4. Verify against contextual constraints (e.g., no fractional people)
            5. Conclude with final numerical answer in boxed format
            
            The solution must be self-contained, rigorous, and pedagogically clear — as if explaining to a Bengali-speaking grade school student.""",
            contexts_list=[refined_linguistic, refined_mathematical, refined_contextual]
        )

        # PHASE 4: SELF-CRITIQUE - Generate adversarial revision
        critiqued_solution = await self.revise(
            instruction="""Play devil's advocate. Critically attack this solution:
            1. Are there alternative interpretations of key phrases?
            2. Could the order of operations be different?
            3. Are units consistently tracked?
            4. Does the answer satisfy all implicit constraints?
            5. What edge cases would break this solution?
            
            Then, revise the solution to address valid criticisms. If no valid criticisms exist, state "Solution is robust." and preserve original.""",
            context=unified_solution
        )

        # PHASE 5: FINAL EXTRACTION - Isolate numerical answer
        final_answer = await self.summarize(
            instruction="""Extract ONLY the final numerical answer from the solution text.
            Rules:
            - Must be a single number (integer or decimal)
            - Remove all units, explanations, and context
            - If multiple numbers exist, select the one that answers the primary question
            - If no clear answer, return "0" as fallback
            
            Example: If solution says "Therefore, total cost is 64 টাকা", return "64".""",
            context=critiqued_solution
        )

        return final_answer.strip()