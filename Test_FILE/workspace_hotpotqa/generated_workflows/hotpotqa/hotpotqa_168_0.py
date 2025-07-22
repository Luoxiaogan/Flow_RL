# Workflow ID: hotpotqa_168_0
# Benchmark: hotpotqa
# Data Indices: [3105, 3810, 3348, 479, 1298]

<operator id="0">
        <instruction>Identify the key entities in the problem statement that need to be matched or connected.</instruction>
        <input>problem</input>
        <output>entities</output>
    </operator>
    <operator id="1">
        <instruction>Extract all relevant contextual information related to the identified entities from the provided context.</instruction>
        <input>entities, context</input>
        <output>contextual_data</output>
    </operator>
    <operator id="2">
        <instruction>Filter and refine the contextual data to eliminate irrelevant details and focus on direct matches or logical connections.</instruction>
        <input>contextual_data</input>
        <output>filtered_data</output>
    </operator>
    <operator id="3">
        <instruction>Map the filtered data to potential answers by evaluating which pieces of information directly satisfy the question's requirements.</instruction>
        <input>filtered_data</input>
        <output>candidate_answers</output>
    </operator>
    <operator id="4">
        <instruction>Validate each candidate answer against the full context to ensure accuracy and avoid false positives due to partial matches.</instruction>
        <input>candidate_answers, context</input>
        <output>validated_answers</output>
    </operator>
    <operator id="5">
        <instruction>Rank the validated answers based on confidence score derived from match strength, uniqueness, and contextual support.</instruction>
        <input>validated_answers</input>
        <output>ranked_answers</output>
    </operator>
    <operator id="6">
        <instruction>Select the top-ranked answer as the final output, ensuring it aligns precisely with the question's query structure.</instruction>
        <input>ranked_answers</input>
        <output>final_answer</output>
    </operator>