# Workflow ID: hotpotqa_34_0
# Benchmark: hotpotqa
# Data Indices: [445, 997, 2503, 2122]

<node id="1">
        <operator>analyze_input</operator>
        <input>problem</input>
        <output>parsed_question, context_info</output>
    </node>
    <node id="2">
        <operator>extract_key_concepts</operator>
        <input>parsed_question, context_info</input>
        <output>concepts</output>
    </node>
    <node id="3">
        <operator>map_to_domain_knowledge</operator>
        <input>concepts</input>
        <output>relevant_facts</output>
    </node>
    <node id="4">
        <operator>validate_and_filter</operator>
        <input>relevant_facts</input>
        <output>filtered_facts</output>
    </node>
    <node id="5">
        <operator>reason_step_by_step</operator>
        <input>filtered_facts</input>
        <output>deduced_answer</output>
    </node>
    <node id="6">
        <operator>verify_consistency</operator>
        <input>deduced_answer, filtered_facts</input>
        <output>final_answer</output>
    </node>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>