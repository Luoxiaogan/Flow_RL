# Workflow ID: hotpotqa_6_0
# Benchmark: hotpotqa
# Data Indices: [256, 3222, 634, 1850, 394]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities and relationships in the problem statement. Extract relevant information that directly answers the question.</instruction>
        <input>problem</input>
        <output>filtered_info</output>
    </agent>
    
    <agent id="2" type="search">
        <instruction>Search for known facts or definitions related to the extracted entities. Focus on confirming the occupation shared by both André Gide and Edith Hamilton.</instruction>
        <input>filtered_info</input>
        <output>occupation_match</output>
    </agent>
    
    <agent id="3" type="verification">
        <instruction>Verify the consistency of the identified occupation with biographical details of both individuals from the context provided.</instruction>
        <input>occupation_match</input>
        <output>verified_occupation</output>
    </agent>
    
    <agent id="4" type="aggregation">
        <instruction>Aggregate the verified occupation as the final answer, ensuring it is precise and matches the question's requirement.</instruction>
        <input>verified_occupation</input>
        <output>final_answer</output>
    </agent>
    
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />