# Workflow ID: hotpotqa_447_0
# Benchmark: hotpotqa
# Data Indices: [1054, 3190, 3357, 3735]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>processed_context</output>
    </operator>
    <operator id="1">
        <instruction>Extract all relevant candidates from the context who might match the criteria of the question.</instruction>
        <input>processed_context</input>
        <output>candidates</output>
    </operator>
    <operator id="2">
        <instruction>Filter candidates based on the specific condition mentioned in the question (e.g., Grammy nomination in 1993).</instruction>
        <input>candidates</input>
        <output>filtered_candidates</output>
    </operator>
    <operator id="3">
        <instruction>Verify that the remaining candidate matches both the role (Runaways member) and the award condition (Grammy nomination for Best Female Rock Vocal Performance in 1993).</instruction>
        <input>filtered_candidates</input>
        <output>final_answer</output>
    </operator>
    <operator id="4">
        <instruction>Double-check the final answer against the full context to ensure no ambiguity or misinterpretation.</instruction>
        <input>final_answer</input>
        <output>verified_answer</output>
    </operator>
    <link from="0" to="1"/>
    <link from="1" to="2"/>
    <link from="2" to="3"/>
    <link from="3" to="4"/>