# Workflow ID: hotpotqa_47_0
# Benchmark: hotpotqa
# Data Indices: [3259, 1090, 3110, 854, 1312]

<agent id="1">
        <instruction>Identify the key entities and relationships in the problem context.</instruction>
        <output>Extract relevant actors, organizations, and their roles from the provided context.</output>
    </agent>
    <agent id="2">
        <instruction>Map the organization to its leadership role based on the context.</instruction>
        <output>Determine the former position of the individual associated with the Atlanta-based EMM provider.</output>
    </agent>
    <agent id="3">
        <instruction>Verify the extracted position against known facts about the organization's leadership.</instruction>
        <output>Confirm the correctness of the former position by cross-referencing with biographical data.</output>
    </agent>
    <agent id="4">
        <instruction>Ensure all steps logically connect to produce a coherent answer.</instruction>
        <output>Finalize the answer as a clear statement of the former position.</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>