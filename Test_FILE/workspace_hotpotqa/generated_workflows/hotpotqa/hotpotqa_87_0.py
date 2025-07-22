# Workflow ID: hotpotqa_87_0
# Benchmark: hotpotqa
# Data Indices: [3297, 3836, 2525, 1348, 646]

<start/>
    <agent id="1" type="extract">
        <instruction>Extract key entities and relationships from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter out irrelevant information and retain only the most pertinent facts for answering the question.</instruction>
    </agent>
    <agent id="3" type="reason">
        <instruction>Reason step-by-step using filtered facts to deduce the correct answer.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Validate the reasoning by cross-checking with the original context to ensure accuracy.</instruction>
    </agent>
    <agent id="5" type="format">
        <instruction>Format the final answer in a clear, concise manner suitable for direct output.</instruction>
    </agent>
    <end/>