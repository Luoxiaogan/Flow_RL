# Workflow ID: hotpotqa_303_0
# Benchmark: hotpotqa
# Data Indices: [1303, 877, 1350, 2209, 2741]

<agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Reason step-by-step about how the extracted entities connect to the answer, eliminating irrelevant information.</instruction>
    </agent>
    <agent id="3" type="verify">
        <instruction>Verify the consistency of the reasoning with known facts in the context. Ensure no contradictions or unsupported claims.</instruction>
    </agent>
    <agent id="4" type="synthesize">
        <instruction>Synthesize the verified reasoning into a clear and concise final answer.</instruction>
    </agent>
    <link from="1" to="2" />
    <link from="2" to="3" />
    <link from="3" to="4" />