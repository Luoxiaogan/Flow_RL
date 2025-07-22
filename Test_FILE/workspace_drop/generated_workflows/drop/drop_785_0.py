# Workflow ID: drop_785_0
# Benchmark: drop
# Data Indices: [1744, 386, 1383, 2475]

<node id="1">
        <input>problem</input>
        <output>extract_question_and_passage</output>
        <operator>extract_question_and_passage</operator>
    </node>
    <node id="2">
        <input>extract_question_and_passage</input>
        <output>identify_key_events</output>
        <operator>identify_key_events</operator>
    </node>
    <node id="3">
        <input>identify_key_events</input>
        <output>locate_specific_information</output>
        <operator>locate_specific_information</operator>
    </node>
    <node id="4">
        <input>locate_specific_information</input>
        <output>validate_answer</output>
        <operator>validate_answer</operator>
    </node>
    <node id="5">
        <input>validate_answer</input>
        <output>final_answer</output>
        <operator>final_answer</operator>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>