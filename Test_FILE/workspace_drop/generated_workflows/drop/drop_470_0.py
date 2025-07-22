# Workflow ID: drop_470_0
# Benchmark: drop
# Data Indices: [2955, 1856, 2273, 1292]

<node id="1">
        <operator>extract_relevant_data</operator>
        <input>problem</input>
        <output>filtered_data</output>
    </node>
    <node id="2">
        <operator>identify_quantities</operator>
        <input>filtered_data</input>
        <output>quantities</output>
    </node>
    <node id="3">
        <operator>perform_calculation</operator>
        <input>quantities</input>
        <output>result</output>
    </node>
    <node id="4">
        <operator>validate_result</operator>
        <input>result</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>