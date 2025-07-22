# Workflow ID: hotpotqa_246_0
# Benchmark: hotpotqa
# Data Indices: [1079, 1672, 744, 3281]

<operator id="1">
        <instruction>Identify the key entities in the problem and determine what is being asked.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>

    <operator id="2">
        <instruction>Extract relevant facts from the context that directly relate to the entities identified.</instruction>
        <input>entity_analysis, context</input>
        <output>fact_extraction</output>
    </operator>

    <operator id="3">
        <instruction>Map the extracted facts to possible answers using logical reasoning.</instruction>
        <input>fact_extraction</input>
        <output>reasoning_path</output>
    </operator>

    <operator id="4">
        <instruction>Validate each potential answer against the context to eliminate contradictions or inaccuracies.</instruction>
        <input>reasoning_path</input>
        <output>answer_candidates</output>
    </operator>

    <operator id="5">
        <instruction>Rank candidates based on confidence level derived from supporting evidence in the context.</instruction>
        <input>answer_candidates</input>
        <output>final_answer</output>
    </operator>

    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>