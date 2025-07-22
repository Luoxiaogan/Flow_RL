# Workflow ID: hotpotqa_207_0
# Benchmark: hotpotqa
# Data Indices: [2189, 1688, 3461, 2899, 1964]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities and their relationships in the problem. Focus on extracting the relevant information needed to solve the question.</instruction>
        <input>problem</input>
        <output>extracted_entities</output>
    </agent>
    
    <agent id="2" type="comparison">
        <instruction>Compare the death dates of the two composers based on the extracted information. Determine which one died earlier.</instruction>
        <input>extracted_entities</input>
        <output>earlier_death</output>
    </agent>
    
    <agent id="3" type="verification">
        <instruction>Verify the accuracy of the comparison by cross-checking the birth and death years from reliable sources or context clues.</instruction>
        <input>extracted_entities</input>
        <output>verified_result</output>
    </agent>
    
    <agent id="4" type="synthesis">
        <instruction>Combine the verified result with a clear explanation of the reasoning process to produce the final answer.</instruction>
        <input>verified_result</input>
        <output>final_answer</output>
    </agent>
    
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />