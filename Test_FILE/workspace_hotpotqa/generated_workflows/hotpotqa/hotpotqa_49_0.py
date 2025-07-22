# Workflow ID: hotpotqa_49_0
# Benchmark: hotpotqa
# Data Indices: [3567, 3669, 323, 575]

<start/>
    <agent id="1" type="reasoning">
        <instruction>Identify the key entities and relationships in the problem. Break down the question into its core components to determine what needs to be found.</instruction>
    </agent>
    <agent id="2" type="retrieval">
        <instruction>Extract relevant information from the context that directly answers the question or provides necessary clues for solving it.</instruction>
    </agent>
    <agent id="3" type="comparison">
        <instruction>Compare the extracted information to determine if both entities (e.g., Brachychiton and Colchicum) are found on the same continent based on geographic distribution data.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify the conclusion by cross-checking with all available geographic data points in the context to ensure accuracy.</instruction>
    </agent>
    <agent id="5" type="synthesis">
        <instruction>Combine the verified result with the original question to produce a clear, concise final answer.</instruction>
    </agent>
    <end/>