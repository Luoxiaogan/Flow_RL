# Workflow ID: hotpotqa_423_0
# Benchmark: hotpotqa
# Data Indices: [1049, 2226, 958, 1248, 3372]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities and their relationships in the problem. Break down the question into smaller components to determine what needs to be compared or analyzed.</instruction>
        <input>problem</input>
        <output>parsed_question</output>
    </agent>
    
    <agent id="2" type="retrieval">
        <instruction>Extract relevant dates or biographical details from the context for each entity mentioned in the parsed question.</instruction>
        <input>parsed_question, context</input>
        <output>entity_dates</output>
    </agent>
    
    <agent id="3" type="comparison">
        <instruction>Compare the birth years of the two individuals to determine who was born first.</instruction>
        <input>entity_dates</input>
        <output>result</output>
    </agent>
    
    <agent id="4" type="verification">
        <instruction>Double-check the comparison logic and ensure that the correct individual is identified as the earlier-born based on verified birth years.</instruction>
        <input>result</input>
        <output>final_answer</output>
    </agent>
    
    <agent id="5" type="formatting">
        <instruction>Format the final answer as a clear, concise statement that directly answers the original question.</instruction>
        <input>final_answer</input>
        <output>formatted_output</output>
    </agent>
    
    <connection>
        <from>1</from>
        <to>2</to>
    </connection>
    
    <connection>
        <from>2</from>
        <to>3</to>
    </connection>
    
    <connection>
        <from>3</from>
        <to>4</to>
    </connection>
    
    <connection>
        <from>4</from>
        <to>5</to>
    </connection>