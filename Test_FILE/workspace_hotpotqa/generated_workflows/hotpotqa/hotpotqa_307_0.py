# Workflow ID: hotpotqa_307_0
# Benchmark: hotpotqa
# Data Indices: [1880, 3076, 3619, 275, 3162]

<node id="1">
        <operator>extract_key_info</operator>
        <input>problem</input>
        <output>key_concepts</output>
    </node>
    <node id="2">
        <operator>identify_relationships</operator>
        <input>key_concepts</input>
        <output>relations</output>
    </node>
    <node id="3">
        <operator>filter_relevant_entities</operator>
        <input>relations</input>
        <output>entities</output>
    </node>
    <node id="4">
        <operator>resolve_entity_attributes</operator>
        <input>entities</input>
        <output>attributes</output>
    </node>
    <node id="5">
        <operator>validate_solution</operator>
        <input>attributes</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>