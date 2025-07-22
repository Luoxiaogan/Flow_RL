# Workflow ID: hotpotqa_162_0
# Benchmark: hotpotqa
# Data Indices: [2399, 2117, 861, 1102]

<agent id="1">
        <instruction>Identify the key entities and their relationships in the problem context.</instruction>
        <output>Extract relevant entities and connections between them.</output>
    </agent>
    <agent id="2">
        <instruction>Process each entity to determine shared attributes or events based on the context.</instruction>
        <output>Identify commonalities such as events, affiliations, or achievements.</output>
    </agent>
    <agent id="3">
        <instruction>Validate the commonality by cross-referencing with known facts from the context.</instruction>
        <output>Confirm whether the identified connection is supported by multiple sources in the text.</output>
    </agent>
    <agent id="4">
        <instruction>Generate a concise summary of the shared trait or event that connects the two individuals.</instruction>
        <output>Final answer: A specific, verifiable commonality between the two subjects.</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>