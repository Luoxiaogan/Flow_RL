# Workflow ID: hotpotqa_495_0
# Benchmark: hotpotqa
# Data Indices: [2013, 17, 3144, 2763]

<agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter out irrelevant entities and focus only on those directly tied to the question's subject.</instruction>
    </agent>
    <agent id="3" type="map">
        <instruction>Map filtered entities to their roles or attributes that answer the question.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Validate that the mapped information matches the question's requirements exactly.</instruction>
    </agent>
    <agent id="5" type="synthesize">
        <instruction>Synthesize the validated information into a coherent final answer.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />
    <edge from="4" to="5" />