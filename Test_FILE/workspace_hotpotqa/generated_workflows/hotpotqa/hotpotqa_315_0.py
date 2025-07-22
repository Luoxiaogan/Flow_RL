# Workflow ID: hotpotqa_315_0
# Benchmark: hotpotqa
# Data Indices: [2015, 1759, 1331, 90, 272]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities in the problem and their relationships. Break down the question into smaller components to determine what needs to be found.</instruction>
    </agent>
    <agent id="2" type="retrieval">
        <instruction>Extract relevant information from the context that directly answers the question. Focus on specific details such as names, dates, or attributes tied to the entities mentioned in the question.</instruction>
    </agent>
    <agent id="3" type="verification">
        <instruction>Validate the extracted information against the question’s requirements. Ensure that the answer satisfies all constraints (e.g., dimensionless quantity, named after a Nobel laureate).</instruction>
    </agent>
    <agent id="4" type="synthesis">
        <instruction>Combine the verified information to form a coherent and precise answer. If multiple pieces of information are needed, ensure they logically connect to produce the final result.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>