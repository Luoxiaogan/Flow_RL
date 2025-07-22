# Workflow ID: hotpotqa_360_0
# Benchmark: hotpotqa
# Data Indices: [2915, 2646, 2029, 129, 1288]

<node id="1">
        <operator>extract_relevant_info</operator>
        <input>problem</input>
        <output>filtered_context</output>
    </node>
    <node id="2">
        <operator>identify_key_entities</operator>
        <input>filtered_context</input>
        <output>key_entities</output>
    </node>
    <node id="3">
        <operator>map_entities_to_attributes</operator>
        <input>key_entities</input>
        <output>entity_attributes</output>
    </node>
    <node id="4">
        <operator>compare_operas</operator>
        <input>entity_attributes</input>
        <output>comparison_result</output>
    </node>
    <node id="5">
        <operator>select_minimum_acts</operator>
        <input>comparison_result</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>