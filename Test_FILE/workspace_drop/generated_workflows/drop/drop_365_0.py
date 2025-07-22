# Workflow ID: drop_365_0
# Benchmark: drop
# Data Indices: [1091, 3266, 433, 1329, 576]

<node id="1" type="input">
        <parameter>problem</parameter>
    </node>
    <node id="2" type="agent">
        <instruction>Extract key numerical data from the passage relevant to the question.</instruction>
        <input>1</input>
        <output>extracted_data</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify the specific value being asked in the question from the extracted data.</instruction>
        <input>2</input>
        <output>target_value</output>
    </node>
    <node id="4" type="agent">
        <instruction>Validate that the target value matches the context of the question and is not an intermediate result.</instruction>
        <input>3</input>
        <output>validated_answer</output>
    </node>
    <node id="5" type="agent">
        <instruction>Format the validated answer into a clear, concise response.</instruction>
        <input>4</input>
        <output>final_output</output>
    </node>
    <node id="6" type="output">
        <parameter>final_output</parameter>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>