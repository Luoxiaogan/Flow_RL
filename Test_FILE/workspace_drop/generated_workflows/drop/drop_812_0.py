# Workflow ID: drop_812_0
# Benchmark: drop
# Data Indices: [1566, 1732, 1602, 178, 2420]

<node id="start" type="input"/>
    <node id="analyze_question" type="agent">
        <instruction>Break down the question step by step to identify what information is needed.</instruction>
    </node>
    <node id="extract_info" type="agent">
        <instruction>From the passage, locate and extract only the relevant data that answers the question.</instruction>
    </node>
    <node id="process_data" type="agent">
        <instruction>Perform necessary calculations or comparisons using the extracted data.</instruction>
    </node>
    <node id="validate" type="agent">
        <instruction>Ensure the result logically follows from the data and matches the question's requirement.</instruction>
    </node>
    <node id="output" type="output"/>
    
    <edge from="start" to="analyze_question"/>
    <edge from="analyze_question" to="extract_info"/>
    <edge from="extract_info" to="process_data"/>
    <edge from="process_data" to="validate"/>
    <edge from="validate" to="output"/>