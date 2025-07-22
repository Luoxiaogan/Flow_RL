# Workflow ID: hotpotqa_427_0
# Benchmark: hotpotqa
# Data Indices: [2157, 3785, 2758, 785]

<agent id="1" type="extract">
        <instruction>Extract key entities and their attributes from the context that might relate to the question.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter entities from agent 1 that match the criteria in the question, such as birth dates or roles.</instruction>
    </agent>
    <agent id="3" type="match">
        <instruction>Match filtered entities to the exact condition in the question (e.g., actor born on September 22, 1987).</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Validate that the matched entity is indeed part of the cast of the film mentioned in the question.</instruction>
    </agent>
    <agent id="5" type="output">
        <instruction>Return the final answer based on validated result from agent 4.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>