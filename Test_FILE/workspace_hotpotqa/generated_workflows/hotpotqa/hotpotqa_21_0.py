# Workflow ID: hotpotqa_21_0
# Benchmark: hotpotqa
# Data Indices: [1802, 2386, 2772, 3115, 812]

<start/>
    <agent id="1" type="question_analysis">
        <instruction>Break down the question step by step to identify key entities and what is being asked.</instruction>
    </agent>
    <agent id="2" type="context_search">
        <instruction>Search for relevant context that directly answers the question. Focus on named entities and specific facts.</instruction>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify that the retrieved information matches the question exactly and is unambiguous.</instruction>
    </agent>
    <agent id="4" type="synthesis">
        <instruction>Combine verified information into a clear, concise final answer.</instruction>
    </agent>
    <end/>
    <edge from="start" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="end"/>