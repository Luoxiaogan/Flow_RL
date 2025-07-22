# Workflow ID: hotpotqa_223_0
# Benchmark: hotpotqa
# Data Indices: [2926, 2470, 2870, 2061, 1005]

<operator id="1">
        <instruction>Identify the key entities and relationships in the problem context to determine what information is needed to answer the question.</instruction>
        <input>problem</input>
        <output>entity_extraction</output>
    </operator>
    
    <operator id="2">
        <instruction>Filter relevant contextual sentences that directly address the question, focusing on the specific date of the election mentioned in relation to Jim Inhofe's re-election.</instruction>
        <input>entity_extraction</input>
        <output>context_filtering</output>
    </operator>
    
    <operator id="3">
        <instruction>Extract the exact date from the filtered context that corresponds to the 1996 United States Senate election in Oklahoma.</instruction>
        <input>context_filtering</input>
        <output>date_extraction</output>
    </operator>
    
    <operator id="4">
        <instruction>Verify that the extracted date matches the description: "incumbent Republican U.S. Senator Jim Inhofe won re-election to his first full term."</instruction>
        <input>date_extraction</input>
        <output>verification</output>
    </operator>
    
    <operator id="5">
        <instruction>Return the verified date as the final answer to the question.</instruction>
        <input>verification</input>
        <output>final_answer</output>
    </operator>
    
    <link from="1" to="2"/>
    <link from="2" to="3"/>
    <link from="3" to="4"/>
    <link from="4" to="5"/>