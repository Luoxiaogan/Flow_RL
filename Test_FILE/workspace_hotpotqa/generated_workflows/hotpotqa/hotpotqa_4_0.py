# Workflow ID: hotpotqa_4_0
# Benchmark: hotpotqa
# Data Indices: [3249, 2096, 1767, 1548, 1512]

<agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the input context.</instruction>
    </agent>
    <agent id="2" type="map">
        <instruction>Map extracted entities to known references or categories (e.g., universities, films, poets).</instruction>
    </agent>
    <agent id="3" type="verify">
        <instruction>Verify consistency between mapped entities and the question's requirements.</instruction>
    </agent>
    <agent id="4" type="resolve">
        <instruction>Resolve the correct answer by cross-checking verified mappings and eliminating mismatches.</instruction>
    </agent>
    <agent id="5" type="validate">
        <instruction>Validate the final answer against all relevant evidence in the context.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>