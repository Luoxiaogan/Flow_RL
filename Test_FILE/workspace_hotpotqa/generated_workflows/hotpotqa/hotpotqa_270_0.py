# Workflow ID: hotpotqa_270_0
# Benchmark: hotpotqa
# Data Indices: [821, 289, 3663, 2136]

<start>
        <operator name="extract_relevant_info" input="problem" output="relevant_info"/>
    </start>

    <operator name="identify_key_entities" input="relevant_info" output="entities"/>
    
    <operator name="map_entities_to_domain" input="entities" output="domain_mapping"/>

    <operator name="validate_domain_consistency" input="domain_mapping" output="consistency_check"/>

    <operator name="generate_conclusion" input="consistency_check" output="final_answer"/>

    <end>
        <operator name="format_output" input="final_answer" output="output"/>
    </end>

    <edge from="start" to="extract_relevant_info"/>
    <edge from="extract_relevant_info" to="identify_key_entities"/>
    <edge from="identify_key_entities" to="map_entities_to_domain"/>
    <edge from="map_entities_to_domain" to="validate_domain_consistency"/>
    <edge from="validate_domain_consistency" to="generate_conclusion"/>
    <edge from="generate_conclusion" to="end"/>
    <edge from="end" to="format_output"/>