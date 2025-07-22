# Workflow ID: hotpotqa_361_0
# Benchmark: hotpotqa
# Data Indices: [1198, 515, 2352, 1652, 2342]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the key entities and relationships in the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="extraction">
        <instruction>Extract only the relevant information about the two entities mentioned in the question from the context provided.</instruction>
    </agent>
    <agent id="3" type="comparison">
        <instruction>Compare the founding years of the two entities extracted in agent 2 to determine which was founded first.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify that the comparison result aligns with the factual data in the context and confirm the correct answer.</instruction>
    </agent>
    <agent id="5" type="output">
        <instruction>Provide the final answer based on the verified result from agent 4, ensuring clarity and correctness.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>