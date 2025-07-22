# Workflow ID: hotpotqa_544_0
# Benchmark: hotpotqa
# Data Indices: [404, 897, 614, 807]

<agent id="1" type="extract">
        <instruction>Extract the key entities and relationships from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Use logical reasoning to connect the extracted entities and determine the correct answer based on the relationships.</instruction>
    </agent>
    <agent id="3" type="verify">
        <instruction>Verify the consistency of the reasoning with the context and ensure no contradictions exist.</instruction>
    </agent>
    <agent id="4" type="synthesize">
        <instruction>Combine the verified result into a clear and concise final answer.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />