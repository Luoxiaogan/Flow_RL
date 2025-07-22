# Workflow ID: hotpotqa_305_0
# Benchmark: hotpotqa
# Data Indices: [3473, 64, 820, 1769, 3472]

<operator id="1" type="agent">
        <instruction>Identify the key entities and relationships in the problem context. Focus on extracting relevant facts that directly answer the question.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Verify the nationality of each named individual by cross-referencing with known biographical data. Ensure accuracy by checking for explicit mentions or logical inferences from the context.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Compare the findings from Operator 1 and 2 to determine if both individuals are American. If not, specify which one is not and provide evidence.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Generate a concise summary that clearly states whether Rob Zombie and Jang Joon-hwan are American, based on the evidence collected. Avoid ambiguity.</instruction>
    </operator>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>