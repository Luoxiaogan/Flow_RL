# Workflow ID: drop_683_0
# Benchmark: drop
# Data Indices: [2540, 3691, 2894, 3221]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>
      Analyze the passage to identify all touchdown plays involving Patrick Chung. Extract the yardage of each touchdown play.
    </instruction>
    <input>problem</input>
    <output>chung_touchdowns</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>
      Sum the yardages from Patrick Chung's two touchdown plays to compute the total yards.
    </instruction>
    <input>chung_touchdowns</input>
    <output>total_yards</output>
  </node>
  
  <node id="4" type="output">
    <input>total_yards</input>
  </node>