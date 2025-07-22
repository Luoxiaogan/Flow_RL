# Workflow ID: hotpotqa_291_0
# Benchmark: hotpotqa
# Data Indices: [1367, 582, 1421, 2728, 3392]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities and relationships in the context that directly answer the question. Focus on extracting only the relevant information needed to solve the problem.</instruction>
    </agent>
    <agent id="2" type="comparison">
        <instruction>Compare the values or attributes of the two entities mentioned in the question using the extracted information. Ensure the comparison is based solely on the provided context.</instruction>
    </agent>
    <agent id="3" type="verification">
        <instruction>Verify the correctness of the comparison by cross-checking with the context. If any ambiguity exists, flag it for resolution.</instruction>
    </agent>
    <agent id="4" type="synthesis">
        <instruction>Combine the verified result from the comparison with the original question to produce a clear and concise final answer.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />