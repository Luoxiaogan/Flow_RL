# Workflow ID: hotpotqa_414_0
# Benchmark: hotpotqa
# Data Indices: [60, 3326, 3096, 1497]

<start/>
    <operator id="1">
        <instruction>Identify the key entities in the problem and their relationships.</instruction>
        <input>problem</input>
        <output>entity_list</output>
    </operator>
    <operator id="2">
        <instruction>Extract relevant contextual clues that directly relate to the question.</instruction>
        <input>entity_list, context</input>
        <output>clue_set</output>
    </operator>
    <operator id="3">
        <instruction>Filter out irrelevant information from the context based on the clue set.</instruction>
        <input>clue_set, context</input>
        <output>filtered_context</output>
    </operator>
    <operator id="4">
        <instruction>Map each clue to a potential answer candidate using logical inference.</instruction>
        <input>filtered_context</input>
        <output>candidate_answers</output>
    </operator>
    <operator id="5">
        <instruction>Validate candidates by cross-referencing with known facts or constraints from the context.</instruction>
        <input>candidate_answers, context</input>
        <output>validated_answers</output>
    </operator>
    <operator id="6">
        <instruction>Rank the validated answers by confidence level based on evidence strength.</instruction>
        <input>validated_answers</input>
        <output>ranked_answers</output>
    </operator>
    <operator id="7">
        <instruction>Select the top-ranked answer as the final solution.</instruction>
        <input>ranked_answers</input>
        <output>final_answer</output>
    </operator>
    <end/>