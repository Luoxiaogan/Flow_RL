# Workflow ID: hotpotqa_243_0
# Benchmark: hotpotqa
# Data Indices: [3066, 3901, 2957, 454, 2407]

<start>
        <task>Initialize problem context and agents</task>
        <next>agent1</next>
    </start>

    <agent1>
        <task>Analyze question and extract key entities</task>
        <next>agent2</next>
    </agent1>

    <agent2>
        <task>Match entities against provided context to find relevant information</task>
        <next>agent3</next>
    </agent2>

    <agent3>
        <task>Validate matches and resolve ambiguity if needed</task>
        <next>agent4</next>
    </agent3>

    <agent4>
        <task>Construct final answer based on validated evidence</task>
        <next>end</next>
    </agent4>

    <end>
        <task>Return structured output with answer and confidence</task>
    </end>