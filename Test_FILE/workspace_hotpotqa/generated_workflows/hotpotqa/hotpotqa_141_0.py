# Workflow ID: hotpotqa_141_0
# Benchmark: hotpotqa
# Data Indices: [2813, 612, 2231, 1271, 2649]

<agent id="1" type="question_analysis">
        <instruction>Break down the question to identify key entities and required information. Focus on the director of Atomic Monster Productions and their ethnic background.</instruction>
    </agent>
    <agent id="2" type="entity_identification">
        <instruction>From the context, locate the director who founded Atomic Monster Productions. Extract relevant details about this person.</instruction>
    </agent>
    <agent id="3" type="ethnic_background_extraction">
        <instruction>Determine the ethnic background of the identified director using available biographical data in the context.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Verify the extracted ethnic background by cross-referencing with any additional contextual clues or known facts about the director.</instruction>
    </agent>
    <agent id="5" type="final_answer_generation">
        <instruction>Generate a concise and accurate final answer based on verified information from previous agents.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>