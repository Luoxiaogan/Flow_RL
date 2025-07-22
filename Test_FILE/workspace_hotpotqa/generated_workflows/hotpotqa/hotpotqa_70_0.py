# Workflow ID: hotpotqa_70_0
# Benchmark: hotpotqa
# Data Indices: [1183, 2931, 2972, 672, 3995]

<operator id="1" type="agent">
        <instruction>Identify the key entities and relationships in the problem statement. Break down the question into its core components to determine what information is needed to solve it.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Extract relevant facts from the context that directly relate to the question. Focus only on data that helps answer the specific query, avoiding unnecessary details.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Compare the extracted facts to identify the correct answer. Ensure logical consistency between the question and the selected evidence.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Verify the solution by cross-checking against the context to eliminate ambiguity or incorrect interpretations.</instruction>
    </operator>
    <operator id="5" type="agent">
        <instruction>Generate a concise and accurate final response based on the verified solution.</instruction>
    </operator>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>