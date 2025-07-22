# Workflow ID: drop_685_0
# Benchmark: drop
# Data Indices: [570, 3109, 738, 2022, 2203]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the passage to identify all scoring plays and their details, focusing on touchdowns and field goals.
        </instruction>
        <output>parsed_events</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            Extract and categorize all touchdown passes from the parsed events. For each, record the player and yardage.
        </instruction>
        <output>touchdown_passes</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            From the touchdown passes, determine the longest one by comparing yardages.
        </instruction>
        <output>longest_touchdown_pass</output>
    </node>
    
    <node id="5" type="agent">
        <instruction>
            Identify all field goals and their yardages. Then, count how many occurred in the first half versus the second half.
        </instruction>
        <output>field_goal_counts</output>
    </node>
    
    <node id="6" type="agent">
        <instruction>
            Determine the longest field goal by comparing yardages of all field goals recorded.
        </instruction>
        <output>longest_field_goal</output>
    </node>
    
    <node id="7" type="agent">
        <instruction>
            Identify which conference both teams belong to based on the team names mentioned in the passage.
        </instruction>
        <output>conference</output>
    </node>
    
    <node id="8" type="agent">
        <instruction>
            Combine the results from all agents: longest touchdown pass, field goal counts, longest field goal, and conference.
        </instruction>
        <output>final_answer</output>
    </node>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="2" to="5"/>
    <edge from="5" to="6"/>
    <edge from="2" to="7"/>
    <edge from="4" to="8"/>
    <edge from="6" to="8"/>
    <edge from="7" to="8"/>