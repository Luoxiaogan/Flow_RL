# Workflow ID: hotpotqa_292_0
# Benchmark: hotpotqa
# Data Indices: [216, 2633, 2849, 284, 3792]

<operator id="0">
        <instruction>Identify the key entities mentioned in the problem and determine what type of information is being requested.</instruction>
        <input>problem</input>
        <output>entity_type, query_focus</output>
    </operator>
    <operator id="1">
        <instruction>Extract all relevant candidates from the context that match the entity type and relate to the query focus.</instruction>
        <input>context, entity_type, query_focus</input>
        <output>candidate_list</output>
    </operator>
    <operator id="2">
        <instruction>Filter candidates based on relevance to the specific question and eliminate any distractors or unrelated mentions.</instruction>
        <input>candidate_list, query_focus</input>
        <output>filtered_candidates</output>
    </operator>
    <operator id="3">
        <instruction>Verify each filtered candidate by cross-checking with the context for explicit confirmation of their role or association.</instruction>
        <input>filtered_candidates, context</input>
        <output>verified_answers</output>
    </operator>
    <operator id="4">
        <instruction>Return the final answer if exactly one verified candidate matches the query. If multiple or none match, return 'No clear answer'.</instruction>
        <input>verified_answers</input>
        <output>final_answer</output>
    </operator>