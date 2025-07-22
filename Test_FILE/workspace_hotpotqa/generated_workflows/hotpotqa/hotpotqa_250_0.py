# Workflow ID: hotpotqa_250_0
# Benchmark: hotpotqa
# Data Indices: [3869, 916, 2719, 2239]

<agent id="1">
        <instruction>Identify the key entities in the context that relate to the question. Focus on names, roles, and specific details mentioned.</instruction>
        <output>Extracted relevant entities: Danai Gurira, The Walking Dead, Eclipsed (play), 2015, Liberian women.</output>
    </agent>
    <agent id="2">
        <instruction>Match the extracted entities to determine which person fits both criteria: known for a role in "The Walking Dead" and wrote a play about Liberian women in 2015.</instruction>
        <output>Confirmed: Danai Gurira is an American actress known for playing Michonne on "The Walking Dead" and wrote the play "Eclipsed" in 2015 about Liberian women.</output>
    </agent>
    <agent id="3">
        <instruction>Verify the information from agent 2 by cross-referencing with the context to ensure accuracy and completeness.</instruction>
        <output>Verified: Context explicitly states Danai Gurira is best known for her role as Michonne on "The Walking Dead" and wrote "Eclipsed", a 2015 play about Liberian women.</output>
    </agent>
    <agent id="4">
        <instruction>Return the final answer based on the verified information from agent 3.</instruction>
        <output>Danai Gurira</output>
    </agent>