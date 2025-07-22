# Workflow ID: hotpotqa_237_0
# Benchmark: hotpotqa
# Data Indices: [994, 1215, 1714, 2629]

<start/>
    <agent id="1" type="reasoning">
        <instruction>Identify the key elements in the question and determine what information is needed to answer it.</instruction>
    </agent>
    <agent id="2" type="retrieval">
        <instruction>Extract relevant details from the provided context that match the identified elements from the first agent.</instruction>
    </agent>
    <agent id="3" type="mapping">
        <instruction>Map the extracted details to form a logical connection between the subject and the answer.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify the logical connection by cross-checking with the context for consistency and accuracy.</instruction>
    </agent>
    <agent id="5" type="synthesis">
        <instruction>Generate the final answer based on the verified logical connection.</instruction>
    </agent>
    <end/>