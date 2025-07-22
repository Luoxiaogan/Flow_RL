# Workflow ID: hotpotqa_586_0
# Benchmark: hotpotqa
# Data Indices: [1646, 3608, 1064, 532, 3040]

<operator id="0">
        <instruction>Identify the key elements in the question: the comic book movie universe, the Irish-American actor, and their prior work on "Agents of S.H.I.E.L.D."</instruction>
        <input>question</input>
        <output>key_elements</output>
    </operator>
    <operator id="1">
        <instruction>Find actors who are Irish-American and have appeared in "Agents of S.H.I.E.L.D."</instruction>
        <input>key_elements</input>
        <output>potential_actors</output>
    </operator>
    <operator id="2">
        <instruction>Determine which of these actors has provided voice work in a comic book movie universe.</instruction>
        <input>potential_actors</input>
        <output>eligible_actor</output>
    </operator>
    <operator id="3">
        <instruction>Verify the comic book movie universe associated with the eligible actor's voice role.</instruction>
        <input>eligible_actor</input>
        <output>universe</output>
    </operator>
    <operator id="4">
        <instruction>Return the name of the comic book movie universe that matches all criteria.</instruction>
        <input>universe</input>
        <output>final_answer</output>
    </operator>