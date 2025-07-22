# Workflow ID: hotpotqa_15_0
# Benchmark: hotpotqa
# Data Indices: [1716, 1408, 732, 549]

<agent id="1">
        <instruction>Identify the key entities and relationships in the context that are relevant to the question. Extract structured information such as names, dates, and affiliations.</instruction>
        <input>context</input>
        <output>structured_data</output>
    </agent>
    
    <agent id="2">
        <instruction>Match the extracted structured data with the question's requirements. Determine which entity directly answers the query based on logical connections.</instruction>
        <input>structured_data</input>
        <output>candidate_answer</output>
    </agent>
    
    <agent id="3">
        <instruction>Validate the candidate answer by cross-referencing it with other parts of the context to ensure accuracy and avoid false positives.</instruction>
        <input>candidate_answer, context</input>
        <output>final_answer</output>
    </agent>
    
    <agent id="4">
        <instruction>Generate a concise explanation for why the final answer is correct, using only the validated information from the context.</instruction>
        <input>final_answer, context</input>
        <output>explanation</output>
    </agent>
    
    <connect from="1" to="2"/>
    <connect from="2" to="3"/>
    <connect from="3" to="4"/>