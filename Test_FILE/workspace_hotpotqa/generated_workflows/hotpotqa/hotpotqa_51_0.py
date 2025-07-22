# Workflow ID: hotpotqa_51_0
# Benchmark: hotpotqa
# Data Indices: [3436, 2925, 597, 3490, 1783]

<operator id="0" type="agent">
        <instruction>Identify the key elements in the question and context that directly relate to the answer. Focus on the subject, the action (produced), and the actor (Teddy Schwarzman).</instruction>
        <input>problem</input>
        <output>filtered_context</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>From the filtered context, locate the movie produced by Teddy Schwarzman that features Benedict Cumberbatch as a character. Extract the name of the character he portrayed.</instruction>
        <input>filtered_context</input>
        <output>character_name</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Verify that the character name matches a known role from a film produced by Teddy Schwarzman. Ensure no other films with Benedict Cumberbatch are mistakenly included.</instruction>
        <input>character_name</input>
        <output>verified_character</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Check if the verified character is indeed played by Benedict Cumberbatch in a movie produced by Teddy Schwarzman. Confirm the accuracy of the match using contextual clues.</instruction>
        <input>verified_character</input>
        <output>final_answer</output>
    </operator>
    <operator id="4" type="agent">
        <instruction>Double-check all previous steps for logical consistency and correctness. If any step fails or is ambiguous, reprocess the relevant data.</instruction>
        <input>final_answer</input>
        <output>final_verification</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>