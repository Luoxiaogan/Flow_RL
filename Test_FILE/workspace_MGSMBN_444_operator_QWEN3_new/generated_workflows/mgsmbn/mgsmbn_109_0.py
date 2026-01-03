# Workflow ID: mgsmbn_109_0
# Benchmark: mgsmbn
# Data Indices: [195]

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

        # PHASE 1: PARALLEL DECOMPOSITION — Extract entities, sequence, and relationships independently
        entity_extraction, sequence_analysis, relationship_modeling = await asyncio.gather(
            self.generate(
                instruction="""You are a Bengali math problem analyst. Extract ALL entities, quantities, and units. 
                Format strictly as:
                Entities: [list of people/objects]
                Quantities: [number + unit + what it refers to, e.g., "1000 মিনিট: monthly plan"]
                Unknown: [what is being asked, e.g., "remaining minutes"]
                Ignore adjectives unless they quantify (e.g., 'double', 'half'). Preserve Bengali units like 'টাকা', 'ঘণ্টা'.""",
                context=""
            ),
            self.generate(
                instruction="""You are a temporal logic expert. Map the sequence of events or dependencies in the problem. 
                Answer in this structure:
                Steps: 
                1. [First event/action with quantities involved]
                2. [Second event...]
                ...
                Dependencies: [What must be calculated before what?]
                Constraints: [Time limits, physical limits, e.g., '30 days', 'no negative items']""",
                context=""
            ),
            self.generate(
                instruction="""You are a mathematical modeler. Identify the core mathematical relationships. 
                Structure your response as:
                Operations Needed: [list: e.g., subtraction, multiplication, proportion]
                Formula Sketch: [equation or step sequence, e.g., "Total - Used = Remaining"]
                Hidden Steps: [any implied calculations, e.g., 'convert days to total minutes']
                Units to Track: [list of units that must be consistent]""",
                context=""
            )
        )

        # PHASE 2: PARALLEL SOLUTION ATTEMPTS + VALIDATION LOOP
        solution_attempts = []
        for i, (extract, seq, model) in enumerate([(entity_extraction, sequence_analysis, relationship_modeling)] * 3):
            # Each attempt uses all three perspectives but with slightly varied emphasis
            attempt = await self.generate(
                instruction=f"""Synthesize the following analyses to compute the answer:
                ENTITY CONTEXT: {extract}
                SEQUENCE CONTEXT: {seq}
                MODEL CONTEXT: {model}
                
                Compute step-by-step:
                1. Initialize known values from entities.
                2. Follow event sequence, applying operations from model.
                3. Track units at every step.
                4. Output ONLY the final numerical answer (no text, no units).
                
                If uncertain, show your reasoning then box the answer as: \\boxed{{number}}""",
                context=f"{extract}\n\n{seq}\n\n{model}"
            )
            solution_attempts.append(attempt)

        # Validation and iterative refinement
        refined_attempts = []
        for attempt in solution_attempts:
            current = attempt
            for _ in range(2):  # Max 2 revisions
                validation = await self.generate(
                    instruction="""Critique this solution:
                    - Are all given numbers used appropriately?
                    - Are units consistent throughout?
                    - Is the answer contextually plausible (e.g., no negative people, fractional buses)?
                    - Are operations applied in correct order?
                    If no issues, respond 'VALID'. Otherwise, list specific fixes needed.""",
                    context=current
                )
                if "VALID" in validation.upper():
                    break
                current = await self.revise(
                    instruction=f"""Revise based on this feedback: {validation}
                    Fix ONLY the identified issues. Preserve correct parts. 
                    Maintain step-by-step clarity. Output only the final numerical answer.""",
                    context=current
                )
            refined_attempts.append(current)

        # PHASE 3: ENSEMBLE SYNTHESIS WITH SCORING
        final_answer = await self.ensemble(
            instruction="""You are the final judge. Select the best answer from the candidates below.
            Score each on:
            1. Completeness (0-10): Used all relevant data?
            2. Consistency (0-10): Units and operations correct?
            3. Plausibility (0-10): Answer makes real-world sense?
            4. Transparency (0-10): Steps traceable?
            Choose the highest total score. If tie, prefer simplest path.
            OUTPUT ONLY THE NUMERICAL ANSWER. NO TEXT. NO UNITS.""",
            contexts_list=refined_attempts
        )

        # Final sanitization: extract only the number (handles \boxed{}, text, etc.)
        sanitized = re.sub(r'[^\d.-]', '', final_answer)
        if '.' in sanitized:
            # Convert to float then back to string to handle decimal cases
            sanitized = str(float(sanitized))
        else:
            sanitized = str(int(float(sanitized))) if sanitized else "0"

        return sanitized