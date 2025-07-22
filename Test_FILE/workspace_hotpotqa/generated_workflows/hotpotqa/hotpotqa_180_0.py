# Workflow ID: hotpotqa_180_0
# Benchmark: hotpotqa
# Data Indices: [1563, 3480, 214, 2792, 143]

<agent id="1" type="extract">
        <instruction>Extract key entities and dates from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="compare">
        <instruction>Compare the birth/death dates of the two individuals mentioned in the question to determine who was born first.</instruction>
    </agent>
    <agent id="3" type="lookup">
        <instruction>Find the population data for the town where the person who died first lived, based on the extracted information.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Verify that the population figure corresponds to the correct year (2000) and location.</instruction>
    </agent>
    <agent id="5" type="aggregate">
        <instruction>Combine the validated population result with the correct answer to the original question.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>