# Workflow ID: hotpotqa_567_0
# Benchmark: hotpotqa
# Data Indices: [703, 3794, 2396, 3423, 3210]

<agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the context that are relevant to the question.</instruction>
    </agent>
    <agent id="2" type="reason">
        <instruction>Use the extracted entities to reason step-by-step about the correct answer based on logical connections in the context.</instruction>
    </agent>
    <agent id="3" type="validate">
        <instruction>Verify the reasoning by cross-checking with other contextual clues or known facts to ensure consistency.</instruction>
    </agent>
    <agent id="4" type="synth">
        <instruction>Combine the validated result into a clear, concise final answer that directly addresses the question.</instruction>
    </agent>
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />