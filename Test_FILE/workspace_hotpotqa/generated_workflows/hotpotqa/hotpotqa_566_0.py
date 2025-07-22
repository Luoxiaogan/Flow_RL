# Workflow ID: hotpotqa_566_0
# Benchmark: hotpotqa
# Data Indices: [1844, 545, 3908, 1414]

<operator id="1">
        <instruction>Identify the key elements in the question: the incomplete work, the composer who left it unfinished, and the Russian composer born in 1904.</instruction>
        <input>problem</input>
        <output>key_elements</output>
    </operator>
    
    <operator id="2">
        <instruction>From the context, find which Russian composer born in 1904 is associated with completing an unfinished work by Prokofiev.</instruction>
        <input>key_elements</input>
        <output>composer_born_1904</output>
    </operator>
    
    <operator id="3">
        <instruction>Verify that the identified composer indeed completed Prokofiev's Cello Concertino based on the provided context.</instruction>
        <input>composer_born_1904</input>
        <output>verification_result</output>
    </operator>
    
    <operator id="4">
        <instruction>Return the name of the Russian composer born in 1904 who completed Prokofiev's Cello Concertino.</instruction>
        <input>verification_result</input>
        <output>final_answer</output>
    </operator>