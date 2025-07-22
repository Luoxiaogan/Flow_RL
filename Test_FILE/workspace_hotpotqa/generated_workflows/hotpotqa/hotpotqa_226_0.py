# Workflow ID: hotpotqa_226_0
# Benchmark: hotpotqa
# Data Indices: [682, 2871, 1763, 1699]

<operator id="0">
        <instruction>Identify the key entities mentioned in the problem and determine which one matches the question.</instruction>
        <input>problem</input>
        <output>candidate_entities</output>
    </operator>
    <operator id="1">
        <instruction>For each candidate entity, verify if it has the attribute or role specified in the question.</instruction>
        <input>candidate_entities</input>
        <output>verified_candidates</output>
    </operator>
    <operator id="2">
        <instruction>Filter out any candidates that do not match the required criteria exactly.</instruction>
        <input>verified_candidates</input>
        <output>final_candidates</output>
    </operator>
    <operator id="3">
        <instruction>Among the final candidates, select the one that is most directly associated with the question's context.</instruction>
        <input>final_candidates</input>
        <output>answer</output>
    </operator>
    <operator id="4">
        <instruction>Double-check the answer by cross-referencing with all provided context to ensure no ambiguity or error.</instruction>
        <input>answer</input>
        <output>validated_answer</output>
    </operator>