# Workflow ID: hotpotqa_7_0
# Benchmark: hotpotqa
# Data Indices: [981, 2004, 490, 3675]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context. Focus on the main subject, associated objects, and their connections.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="1">
        <instruction>Extract all relevant named entities from the context that could answer the question. Prioritize those directly linked to the query.</instruction>
        <input>entity_list</input>
        <output>candidate_entities</output>
    </operator>
    <operator id="2">
        <instruction>Filter candidates based on temporal, categorical, or positional relevance to the question. Eliminate irrelevant entities using logical constraints.</instruction>
        <input>candidate_entities</input>
        <output>filtered_candidates</output>
    </operator>
    <operator id="3">
        <instruction>Verify each filtered candidate by cross-referencing with contextual clues such as roles, affiliations, or events mentioned in the text.</instruction>
        <input>filtered_candidates</input>
        <output>verified_answers</output>
    </operator>
    <operator id="4">
        <instruction>Ensure that only one valid answer remains after verification. If multiple exist, identify the most specific or uniquely tied entity.</instruction>
        <input>verified_answers</input>
        <output>final_answer</output>
    </operator>