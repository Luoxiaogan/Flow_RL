# Workflow ID: drop_146_0
# Benchmark: drop
# Data Indices: [3842, 392, 3438, 3414, 1806]

<node id="1">
        <input>problem</input>
        <output>extract_question_and_passage</output>
        <operator>extract_question_and_passage</operator>
    </node>
    <node id="2">
        <input>extract_question_and_passage</input>
        <output>identify_answer_type</output>
        <operator>identify_answer_type</operator>
    </node>
    <node id="3">
        <input>extract_question_and_passage</input>
        <output>locate_context_in_passage</output>
        <operator>locate_context_in_passage</operator>
    </node>
    <node id="4">
        <input>locate_context_in_passage</input>
        <output>parse_numerical_data</output>
        <operator>parse_numerical_data</operator>
    </node>
    <node id="5">
        <input>parse_numerical_data</input>
        <output>validate_answer</output>
        <operator>validate_answer</operator>
    </node>
    <node id="6">
        <input>validate_answer</input>
        <output>final_answer</output>
        <operator>final_answer</operator>
    </node>
    <edge from="1" to="2"/>
    <edge from="1" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>