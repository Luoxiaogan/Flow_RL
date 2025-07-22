# Workflow ID: hotpotqa_498_0
# Benchmark: hotpotqa
# Data Indices: [2513, 2333, 1461, 3805]

<operator id="0">
        <instruction>Identify the key entities in the problem context that relate to the question.</instruction>
        <input>problem</input>
        <output>entities</output>
    </operator>
    <operator id="1">
        <instruction>Filter entities that match the criteria of being an Australian hard rock band.</instruction>
        <input>entities</input>
        <output>australian_bands</output>
    </operator>
    <operator id="2">
        <instruction>From the filtered bands, find which one had their music mixed by Mike Fraser.</instruction>
        <input>australian_bands</input>
        <output>band_with_fraser</output>
    </operator>
    <operator id="3">
        <instruction>Verify if the identified band is indeed Australian and known for hard rock.</instruction>
        <input>band_with_fraser</input>
        <output>final_answer</output>
    </operator>