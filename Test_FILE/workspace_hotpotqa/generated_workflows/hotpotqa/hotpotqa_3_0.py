# Workflow ID: hotpotqa_3_0
# Benchmark: hotpotqa
# Data Indices: [1984, 1744, 2120, 893]

<operator id="1" type="agent">
        <instruction>Identify the key elements in the question and determine the relevant domain (e.g., sports, history, entertainment).</instruction>
        <input>problem</input>
        <output>domain, key_terms</output>
    </operator>

    <operator id="2" type="agent">
        <instruction>Extract all candidate entities from the context that match the domain and key terms. Focus on names, roles, or affiliations mentioned.</instruction>
        <input>context, domain, key_terms</input>
        <output>candidates</output>
    </operator>

    <operator id="3" type="agent">
        <instruction>Filter candidates based on specific criteria from the question: e.g., left-handed bowler, joined Kent County Cricket Club in 2011.</instruction>
        <input>candidates</input>
        <output>filtered_candidates</output>
    </operator>

    <operator id="4" type="agent">
        <instruction>Validate each filtered candidate against the full context to confirm exact match with all conditions in the question.</instruction>
        <input>filtered_candidates, context</input>
        <output>valid_candidate</output>
    </output>