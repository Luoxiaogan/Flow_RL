# Workflow ID: drop_548_0
# Benchmark: drop
# Data Indices: [2961, 1630, 2978, 3865]

<agent id="1">
        <instruction>Identify the key entities and relationships in the passage that are relevant to answering the question.</instruction>
        <output>Extract named entities (e.g., people, teams, events) and their roles or actions.</output>
    </agent>
    <agent id="2">
        <instruction>Map each entity to its role in the context of the question—focus only on what is directly needed to answer.</instruction>
        <output>Filter and structure relevant data based on the question's focus (e.g., who, what, how much).</output>
    </agent>
    <agent id="3">
        <instruction>Apply logical reasoning: if multiple pieces of evidence exist, determine which one resolves the question definitively.</instruction>
        <output>Resolve ambiguity by selecting the most precise match or calculating derived values (e.g., sum, difference).</output>
    </agent>
    <agent id="4">
        <instruction>Validate the final answer against all extracted facts to ensure no contradictions or omissions.</instruction>
        <output>Return the correct, unambiguous answer to the question.</output>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>