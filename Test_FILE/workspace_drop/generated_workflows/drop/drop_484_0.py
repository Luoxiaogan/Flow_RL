# Workflow ID: drop_484_0
# Benchmark: drop
# Data Indices: [1934, 3361, 1170, 3759, 2257]

<node id="1">
        <operator>extract_relevant_data</operator>
        <input>problem</input>
        <output>raw_data</output>
    </node>
    <node id="2">
        <operator>parse_numbers</operator>
        <input>raw_data</input>
        <output>numerical_values</output>
    </node>
    <node id="3">
        <operator>apply_math_operation</operator>
        <input>numerical_values</input>
        <output>intermediate_result</output>
    </node>
    <node id="4">
        <operator>validate_solution</operator>
        <input>intermediate_result</input>
        <output>final_answer</output>
    </node>
    <node id="5">
        <operator>format_output</operator>
        <input>final_answer</input>
        <output>formatted_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>