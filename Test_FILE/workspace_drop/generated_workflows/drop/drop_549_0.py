# Workflow ID: drop_549_0
# Benchmark: drop
# Data Indices: [2832, 3803, 431, 1940]

<agent id="1" type="extract">
        <instruction>Extract the relevant numerical data from the passage that pertains to the question.</instruction>
    </agent>
    <agent id="2" type="compute">
        <instruction>Perform the necessary calculation based on the extracted data to answer the question.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Verify the correctness of the computed result by cross-checking with the original passage.</instruction>
    </agent>
    <agent id="4" type="format">
        <instruction>Format the validated result into a clear and concise final answer.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />