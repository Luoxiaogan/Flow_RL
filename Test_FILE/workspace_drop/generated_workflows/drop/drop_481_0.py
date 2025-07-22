# Workflow ID: drop_481_0
# Benchmark: drop
# Data Indices: [3499, 2524, 670, 1285, 1487]

<node id="1">
        <operator>extract_relevant_data</operator>
        <input>problem</input>
        <output>raw_data</output>
    </node>
    <node id="2">
        <operator>identify_question_type</operator>
        <input>raw_data</input>
        <output>question_category</output>
    </node>
    <node id="3">
        <operator>parse_numerical_values</operator>
        <input>raw_data</input>
        <output>numerical_data</output>
    </node>
    <node id="4">
        <operator>apply_mathematical_operation</operator>
        <input>numerical_data, question_category</input>
        <output>intermediate_result</output>
    </node>
    <node id="5">
        <operator>validate_solution</operator>
        <input>intermediate_result, raw_data</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="3"/>
    <edge from="2" to="4"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>