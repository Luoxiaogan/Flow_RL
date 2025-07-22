# Workflow ID: drop_142_0
# Benchmark: drop
# Data Indices: [496, 3925, 2660, 1115, 3758]

<node id="1" type="input">
        <prompt>Extract the relevant information from the passage to answer the question.</prompt>
    </node>
    <node id="2" type="process">
        <prompt>Identify the key details related to the subject of the question (e.g., player name, event, statistic).</prompt>
    </node>
    <node id="3" type="process">
        <prompt>Locate all instances where the subject is mentioned in relation to the requested metric (e.g., touchdown passes).</prompt>
    </node>
    <node id="4" type="compute">
        <prompt>Sum the values associated with the metric (e.g., yardage or count) for the subject.</prompt>
    </node>
    <node id="5" type="output">
        <prompt>Return the computed result as the final answer.</prompt>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>