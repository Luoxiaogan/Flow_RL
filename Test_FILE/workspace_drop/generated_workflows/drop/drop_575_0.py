# Workflow ID: drop_575_0
# Benchmark: drop
# Data Indices: [2629, 1594, 1635, 3424, 561]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all instances of field goal attempts and successful conversions.</instruction>
    <input>problem</input>
    <output>field_goal_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>From the extracted field goal data, determine how many field goals were successfully converted by Shaun Suisham.</instruction>
    <input>field_goal_data</input>
    <output>successful_conversions</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Verify that only successful field goals are counted — ignore missed or attempted but unsuccessful kicks.</instruction>
    <input>successful_conversions</input>
    <output>validated_successes</output>
  </node>
  
  <node id="5" type="output">
    <input>validated_successes</input>
    <output>final_answer</output>
  </node>