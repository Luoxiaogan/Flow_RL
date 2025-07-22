# Workflow ID: drop_88_0
# Benchmark: drop
# Data Indices: [3041, 658, 2771, 2004]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the passage. Focus on cities and population distribution.</instruction>
        <input>1</input>
        <output>entities_and_relationships</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Extract numerical data about Armenian populations in each city from the passage.</instruction>
        <input>2</input>
        <output>city_populations</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Calculate percentages for each city to determine which has the highest proportion of Armenians.</instruction>
        <input>3</input>
        <output>percentages</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>Compare the percentages to identify the city with the largest share of Armenians.</instruction>
        <input>4</input>
        <output>most_armenian_city</output>
    </node>
    
    <node id="6" type="output">
        <input>5</input>
        <output>result</output>
    </node>