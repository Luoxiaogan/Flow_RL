# Workflow ID: hotpotqa_597_0
# Benchmark: hotpotqa
# Data Indices: [2002, 1365, 2916, 3506]

<start>
        <task>Identify the core question and relevant context</task>
        <next>extract_relevant_info</next>
    </start>

    <extract_relevant_info>
        <task>Extract key facts from the context that directly answer the question</task>
        <next>analyze_comparison</next>
    </extract_relevant_info>

    <analyze_comparison>
        <task>Compare the number of films directed by each person using extracted data</task>
        <next>generate_answer</next>
    </analyze_comparison>

    <generate_answer>
        <task>Determine who directed more films based on analysis</task>
        <next>end</next>
    </generate_answer>

    <end>
        <task>Return final answer as a string</task>
    </end>