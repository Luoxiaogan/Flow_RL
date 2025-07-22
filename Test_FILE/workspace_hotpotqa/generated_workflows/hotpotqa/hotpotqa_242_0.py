# Workflow ID: hotpotqa_242_0
# Benchmark: hotpotqa
# Data Indices: [3846, 2043, 1184, 1343, 2462]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the correct film directed by John Woo in 1996.</instruction>
        <input>problem</input>
        <output>candidate_film</output>
    </agent>
    <agent id="2" type="filter">
        <instruction>From the list of films directed by John Woo, filter for those released in 1996.</instruction>
        <input>candidate_film</input>
        <output>filtered_film</output>
    </agent>
    <agent id="3" type="verify">
        <instruction>Verify that the film is an American action film and matches the description provided in the question.</instruction>
        <input>filtered_film</input>
        <output>final_answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>