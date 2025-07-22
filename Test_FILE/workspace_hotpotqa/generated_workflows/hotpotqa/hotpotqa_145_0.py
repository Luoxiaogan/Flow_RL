# Workflow ID: hotpotqa_145_0
# Benchmark: hotpotqa
# Data Indices: [2605, 1650, 166, 273]

<operator id="0">
        <instruction>Identify the key entity in the question and locate its relevant context.</instruction>
        <input>problem</input>
        <output>entity_context</output>
    </operator>
    <operator id="1">
        <instruction>Extract the specific attribute or relationship from the context that directly answers the question.</instruction>
        <input>entity_context</input>
        <output>answer_attribute</output>
    </operator>
    <operator id="2">
        <instruction>Verify the extracted attribute against known geographic or administrative boundaries to ensure accuracy.</instruction>
        <input>answer_attribute</input>
        <output>validated_answer</output>
    </operator>
    <operator id="3">
        <instruction>Format the validated answer into a clear, concise response suitable for direct output.</instruction>
        <input>validated_answer</input>
        <output>final_output</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>