# Workflow ID: hotpotqa_179_0
# Benchmark: hotpotqa
# Data Indices: [2489, 1720, 3579, 1828, 3918]

<operator id="1" type="extract">
        <instruction>Identify the key entities and relationships in the problem context. Focus on the main subject, its attributes, and any relevant connections.</instruction>
    </operator>
    <operator id="2" type="filter">
        <instruction>From the extracted entities, filter out only those directly related to the question being asked. Ignore irrelevant details.</instruction>
    </operator>
    <operator id="3" type="map">
        <instruction>Map the filtered entities to possible candidate answers by aligning them with known facts or patterns in the data.</instruction>
    </operator>
    <operator id="4" type="validate">
        <instruction>Validate each candidate answer against the context to ensure it is supported by evidence. Eliminate unsupported options.</instruction>
    </operator>
    <operator id="5" type="resolve">
        <instruction>Resolve the final answer by selecting the candidate that best satisfies all constraints and matches the query precisely.</instruction>
    </operator>
    <operator id="6" type="verify">
        <instruction>Verify the correctness of the resolved answer by cross-checking with the original context to avoid errors from misinterpretation.</instruction>
    </operator>
    <operator id="7" type="output">
        <instruction>Output the final answer as a concise, clear response based on the verified result.</instruction>
    </operator>