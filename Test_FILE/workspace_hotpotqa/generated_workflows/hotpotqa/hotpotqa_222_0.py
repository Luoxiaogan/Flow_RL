# Workflow ID: hotpotqa_222_0
# Benchmark: hotpotqa
# Data Indices: [2000, 2104, 371, 3215]

<agent id="1" type="reasoning">
        <instruction>Think step by step to identify the key information needed to solve this problem. Break down the question and locate relevant context.</instruction>
    </agent>
    <agent id="2" type="extraction">
        <instruction>From the provided context, extract only the necessary facts that directly answer the question. Avoid including irrelevant details.</instruction>
    </agent>
    <agent id="3" type="verification">
        <instruction>Check if the extracted information is sufficient and accurate. If not, revisit the context to find missing pieces.</instruction>
    </agent>
    <agent id="4" type="synthesis">
        <instruction>Combine the verified information into a clear and concise final answer that directly addresses the question.</instruction>
    </agent>
    <agent id="5" type="validation">
        <instruction>Validate the final answer against the original question to ensure it fully resolves the query without ambiguity.</instruction>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>