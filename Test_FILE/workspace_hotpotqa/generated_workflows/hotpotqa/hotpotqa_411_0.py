# Workflow ID: hotpotqa_411_0
# Benchmark: hotpotqa
# Data Indices: [1418, 3419, 2876, 1676, 202]

<start/>
    <operator id="1">
        <instruction>Identify the key entities and their relationships in the context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>
    <operator id="2">
        <instruction>Extract relevant facts from the context that directly relate to the question being asked.</instruction>
        <input>entity_analysis</input>
        <output>fact_extraction</output>
    </operator>
    <operator id="3">
        <instruction>Validate the extracted facts against known data or logical constraints to ensure accuracy.</instruction>
        <input>fact_extraction</input>
        <output>validation</output>
    </operator>
    <operator id="4">
        <instruction>Use the validated facts to compute the final answer by applying domain-specific logic (e.g., chronology, classification).</instruction>
        <input>validation</input>
        <output>final_answer</output>
    </operator>
    <end/>
    <edge from="start" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="end"/>