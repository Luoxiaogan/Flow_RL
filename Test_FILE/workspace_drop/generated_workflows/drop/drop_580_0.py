# Workflow ID: drop_580_0
# Benchmark: drop
# Data Indices: [77, 814, 1352, 1452]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key events in the passage related to touchdowns scored due to turnovers. Focus on plays where a turnover (interception or fumble) led directly to a touchdown.</instruction>
    <param name="input">1</param>
    <output>turnover_touchdowns</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract all instances where a touchdown was scored as a result of a turnover. List each such play with the team and player involved.</instruction>
    <param name="input">2</param>
    <output>formatted_turnovers</output>
  </node>
  <node id="4" type="operator">
    <instruction>Count the number of touchdown passes that resulted from turnovers by filtering for plays where an interception was returned for a touchdown.</instruction>
    <param name="input">3</param>
    <output>count</output>
  </node>
  <node id="5" type="output">
    <param name="input">4</param>
    <param name="output">final_answer</param>
  </node>