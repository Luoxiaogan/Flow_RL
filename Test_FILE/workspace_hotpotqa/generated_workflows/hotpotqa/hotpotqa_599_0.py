# Workflow ID: hotpotqa_599_0
# Benchmark: hotpotqa
# Data Indices: [2783, 2275, 709, 908]

<agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the context that may relate to the question.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter extracted entities to focus only on those relevant to the specific question being asked.</instruction>
    </agent>
    <agent id="3" type="map">
        <instruction>Map filtered entities to possible answers by identifying direct or indirect connections to the query.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Validate each candidate answer against the context for accuracy and relevance.</instruction>
    </agent>
    <agent id="5" type="ensemble">
        <instruction>Combine validated results using a simple majority or consensus rule to produce the final answer.</instruction>
    </agent>