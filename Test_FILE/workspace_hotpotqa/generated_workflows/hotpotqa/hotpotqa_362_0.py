# Workflow ID: hotpotqa_362_0
# Benchmark: hotpotqa
# Data Indices: [988, 3011, 984, 377, 847]

<operator id="0">
        <instruction>Identify the core question and extract key entities from the problem statement.</instruction>
        <input>problem</input>
        <output>key_entities, question</output>
    </operator>
    <operator id="1">
        <instruction>Search for contextual clues in the provided text that directly relate to the key entities.</instruction>
        <input>key_entities, context</input>
        <output>relevant_clues</output>
    </operator>
    <operator id="2">
        <instruction>Validate each clue against known facts or logical consistency to eliminate false leads.</instruction>
        <input>relevant_clues</input>
        <output>validated_clues</output>
    </operator>
    <operator id="3">
        <instruction>Use step-by-step reasoning to connect validated clues into a coherent answer.</instruction>
        <input>validated_clues</input>
        <output>reasoning_chain</output>
    </operator>
    <operator id="4">
        <instruction>Formulate the final answer based on the reasoning chain, ensuring it matches the original question.</instruction>
        <input>reasoning_chain</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>