# Workflow ID: drop_122_0
# Benchmark: drop
# Data Indices: [3564, 3113, 3881, 259]

<node id="1">
        <operator>extract_relevant_info</operator>
        <input>problem</input>
        <output>filtered_info</output>
    </node>
    <node id="2">
        <operator>identify_question_type</operator>
        <input>filtered_info</input>
        <output>question_category</output>
    </node>
    <node id="3">
        <operator>locate_answer_in_context</operator>
        <input>filtered_info, question_category</input>
        <output>raw_answer</output>
    </node>
    <node id="4">
        <operator>validate_answer</operator>
        <input>raw_answer, question_category</input>
        <output>validated_answer</output>
    </node>
    <node id="5">
        <operator>format_output</operator>
        <input>validated_answer</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>