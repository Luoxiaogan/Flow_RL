# Workflow ID: drop_175_0
# Benchmark: drop
# Data Indices: [865, 3308, 452, 74, 1467]

<node id="1">
        <operator>extract_relevant_info</operator>
        <input>problem</input>
        <output>filtered_data</output>
    </node>
    <node id="2">
        <operator>identify_question_type</operator>
        <input>filtered_data</input>
        <output>question_category</output>
    </node>
    <node id="3">
        <operator>apply_mathematical_operation</operator>
        <input>question_category, filtered_data</input>
        <output>intermediate_result</output>
    </node>
    <node id="4">
        <operator>validate_solution</operator>
        <input>intermediate_result</input>
        <output>final_answer</output>
    </node>
    <node id="5">
        <operator>generate_explanation</operator>
        <input>final_answer, question_category</input>
        <output>explanation</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>