# Workflow ID: hotpotqa_31_0
# Benchmark: hotpotqa
# Data Indices: [3285, 2149, 337, 146]

<operator id="0">
        <instruction>Identify the key entities and relationships in the input context to determine the correct answer.</instruction>
        <input>problem</input>
        <output>entity_analysis</output>
    </operator>
    <operator id="1">
        <instruction>Extract candidate answers from the context based on entity analysis, focusing only on relevant details for the question.</instruction>
        <input>entity_analysis</input>
        <output>candidates</output>
    </operator>
    <operator id="2">
        <instruction>Validate each candidate by cross-referencing with known facts or logical consistency within the context.</instruction>
        <input>candidates</input>
        <output>validated_candidates</output>
    </operator>
    <operator id="3">
        <instruction>Filter out incorrect candidates using contextual clues and eliminate distractors that are similar but not correct.</instruction>
        <input>validated_candidates</input>
        <output>filtered_candidates</output>
    </operator>
    <operator id="4">
        <instruction>Rank remaining candidates by relevance and confidence level derived from supporting evidence in the context.</instruction>
        <input>filtered_candidates</input>
        <output>ranked_candidates</output>
    </operator>
    <operator id="5">
        <instruction>Select the top-ranked candidate as the final answer based on strongest contextual support.</instruction>
        <input>ranked_candidates</input>
        <output>final_answer</output>
    </operator>