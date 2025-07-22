# Workflow ID: hotpotqa_306_0
# Benchmark: hotpotqa
# Data Indices: [2031, 517, 441, 1864, 704]

<node id="1">
        <operator>extract_context</operator>
        <input>problem</input>
        <output>context_data</output>
    </node>
    <node id="2">
        <operator>identify_key_entities</operator>
        <input>context_data</input>
        <output>entities</output>
    </node>
    <node id="3">
        <operator>map_entities_to_relations</operator>
        <input>entities</input>
        <output>relations</output>
    </node>
    <node id="4">
        <operator>validate_relations</operator>
        <input>relations</input>
        <output>valid_relations</output>
    </node>
    <node id="5">
        <operator>generate_answer</operator>
        <input>valid_relations</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>