# Workflow ID: hotpotqa_471_0
# Benchmark: hotpotqa
# Data Indices: [728, 2575, 3897, 247]

<operator id="1">
        <instruction>Identify the key entities in the question and context that relate to the actress regarded as the greatest of all time.</instruction>
        <input>problem</input>
        <output>selected_entities</output>
    </operator>
    <operator id="2">
        <instruction>From the selected entities, determine which film featured the actress who is widely considered the greatest actress of all time.</instruction>
        <input>selected_entities</input>
        <output>film_title</output>
    </operator>
    <operator id="3">
        <instruction>Classify the genre or type of the film identified in the previous step based on its plot, themes, and production details.</instruction>
        <input>film_title</input>
        <output>film_type</output>
    </operator>
    <operator id="4">
        <instruction>Verify the classification by cross-referencing with known genres associated with the actress's most acclaimed roles.</instruction>
        <input>film_title, film_type</input>
        <output>verified_type</output>
    </operator>
    <operator id="5">
        <instruction>Return the verified type of film that featured the greatest actress of all time.</instruction>
        <input>verified_type</input>
        <output>final_answer</output>
    </operator>