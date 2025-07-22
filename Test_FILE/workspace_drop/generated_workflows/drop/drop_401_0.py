# Workflow ID: drop_401_0
# Benchmark: drop
# Data Indices: [3861, 2931, 3896, 3976, 3018]

<agent id="1">
        <instruction>Identify the key numerical data points in the passage relevant to the question.</instruction>
        <input>problem</input>
        <output>list_of_numbers</output>
    </agent>
    
    <agent id="2">
        <instruction>Extract all touchdown distances or scores mentioned in the passage, depending on the question type.</instruction>
        <input>problem</input>
        <output>touchdowns_or_scores</output>
    </agent>
    
    <agent id="3">
        <instruction>Filter and sort the relevant values (e.g., yardages for touchdowns) to find the shortest ones.</instruction>
        <input>touchdowns_or_scores</input>
        <output>sorted_shortest</output>
    </agent>
    
    <agent id="4">
        <instruction>Map the shortest yardage values to their corresponding players from the passage.</instruction>
        <input>sorted_shortest</input>
        <output>player_mapping</output>
    </agent>
    
    <agent id="5">
        <instruction>Combine the player mappings into a final answer that identifies the two shortest touchdowns.</instruction>
        <input>player_mapping</input>
        <output>final_answer</output>
    </agent>
    
    <connect>
        <from>1</from>
        <to>3</to>
    </connect>
    
    <connect>
        <from>2</from>
        <to>3</to>
    </connect>
    
    <connect>
        <from>3</from>
        <to>4</to>
    </connect>
    
    <connect>
        <from>4</from>
        <to>5</to>
    </connect>