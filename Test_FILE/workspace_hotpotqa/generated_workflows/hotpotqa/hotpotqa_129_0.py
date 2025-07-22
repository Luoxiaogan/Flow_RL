# Workflow ID: hotpotqa_129_0
# Benchmark: hotpotqa
# Data Indices: [2367, 2651, 1550, 2112]

<agent id="1">
        <instruction>Identify the key entity in the question and locate its relevant context.</instruction>
        <input>problem</input>
        <output>entity_context</output>
    </agent>
    <agent id="2">
        <instruction>Extract the foundational details of the entity from the context, such as location, date, or related events.</instruction>
        <input>entity_context</input>
        <output>foundational_details</output>
    </agent>
    <agent id="3">
        <instruction>Verify if the extracted details directly answer the question or require further inference.</instruction>
        <input>foundational_details</input>
        <output>verification_result</output>
    </agent>
    <agent id="4">
        <instruction>If verification requires additional information, retrieve it from the broader context using logical reasoning.</instruction>
        <input>verification_result</input>
        <output>additional_info</output>
    </agent>
    <agent id="5">
        <instruction>Combine all verified facts to construct a precise and complete answer.</instruction>
        <input>additional_info</input>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>