# Workflow ID: drop_404_0
# Benchmark: drop
# Data Indices: [2717, 3725, 1075, 2923]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Identify the key numerical data points in the passage related to the question. Focus on scores, time periods (like halftime), and teams involved.</instruction>
        <input>1</input>
        <output>key_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Extract the score at halftime from the key data. If multiple scores are mentioned, determine which one corresponds to the team asked about in the question.</instruction>
        <input>2</input>
        <output>halftime_score</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Calculate the difference between the two teams' scores at halftime if the question asks for a point differential. Otherwise, return the exact value if it's asking for a single team's score.</instruction>
        <input>3</input>
        <output>point_difference</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
        <output>final_answer</output>
    </node>