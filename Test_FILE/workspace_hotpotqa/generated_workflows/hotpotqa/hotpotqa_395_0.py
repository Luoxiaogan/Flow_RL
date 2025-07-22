# Workflow ID: hotpotqa_395_0
# Benchmark: hotpotqa
# Data Indices: [3966, 664, 1039, 3665, 1101]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context that directly answer the question.</instruction>
        <input>problem</input>
        <output>entity_candidates</output>
    </operator>
    <operator id="1">
        <instruction>Filter candidates to only those that match the specific role or attribute mentioned in the question.</instruction>
        <input>entity_candidates</input>
        <output>filtered_entities</output>
    </operator>
    <operator id="2">
        <instruction>Validate each filtered entity by cross-referencing with known facts or authoritative sources in the context.</instruction>
        <input>filtered_entities</input>
        <output>validated_entities</output>
    </operator>
    <operator id="3">
        <instruction>Rank the validated entities based on relevance, specificity, and contextual strength of evidence.</instruction>
        <input>validated_entities</input>
        <output>ranked_entities</output>
    </operator>
    <operator id="4">
        <instruction>Extract the final answer from the top-ranked entity, ensuring it precisely matches the question's requirement.</instruction>
        <input>ranked_entities</input>
        <output>final_answer</output>
    </operator>
    <operator id="5">
        <instruction>Double-check the final answer against all prior steps to prevent logical inconsistencies or misinterpretations.</instruction>
        <input>final_answer</input>
        <output>verified_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>