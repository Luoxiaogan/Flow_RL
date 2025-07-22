# Workflow ID: hotpotqa_328_0
# Benchmark: hotpotqa
# Data Indices: [2499, 3129, 2796, 1574, 619]

<operator id="0">
        <instruction>Identify the key entities in the question and context that are directly relevant to answering the query.</instruction>
        <input>question, context</input>
        <output>relevant_entities</output>
    </operator>
    <operator id="1">
        <instruction>Extract specific details from the context that connect the entities identified in step 0. Focus on relationships or attributes that answer the question.</instruction>
        <input>relevant_entities, context</input>
        <output>connections</output>
    </operator>
    <operator id="2">
        <instruction>Validate each connection against the question to determine which one uniquely satisfies the criteria (e.g., actor, film, year, company).</instruction>
        <input>connections, question</input>
        <output>valid_solutions</output>
    </operator>
    <operator id="3">
        <instruction>For each valid solution, check if it matches the expected format of the answer (e.g., a name, a title, etc.). If multiple match, ensure they all satisfy the question's constraints.</instruction>
        <input>valid_solutions</input>
        <output>final_answer_candidates</output>
    </operator>
    <operator id="4">
        <instruction>Return the final answer based on the most precise and unambiguous candidate from the previous step.</instruction>
        <input>final_answer_candidates</input>
        <output>answer</output>
    </operator>