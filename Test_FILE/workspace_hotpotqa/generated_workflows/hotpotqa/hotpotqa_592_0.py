# Workflow ID: hotpotqa_592_0
# Benchmark: hotpotqa
# Data Indices: [3651, 3973, 949, 2509]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context that are relevant to the question.</instruction>
        <input>problem</input>
        <output>filtered_context</output>
    </operator>
    <operator id="1">
        <instruction>Extract specific information from the filtered context that directly answers the question.</instruction>
        <input>filtered_context</input>
        <output>answer_clue</output>
    </operator>
    <operator id="2">
        <instruction>Verify the extracted clue against known facts or logical consistency to ensure accuracy.</instruction>
        <input>answer_clue</input>
        <output>validated_answer</output>
    </operator>
    <operator id="3">
        <instruction>Format the validated answer into a concise, final response suitable for the given question.</instruction>
        <input>validated_answer</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>