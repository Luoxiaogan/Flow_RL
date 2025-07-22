# Workflow ID: hotpotqa_25_0
# Benchmark: hotpotqa
# Data Indices: [803, 1570, 3363, 1321, 2259]

<agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the input context.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Identify the specific question and determine which extracted entities are relevant to answering it.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Verify that the answer derived from the context matches the question exactly, without ambiguity or extra information.</instruction>
    </agent>
    <agent id="4" type="synthesize">
        <instruction>Combine validated information into a concise, accurate final answer.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />