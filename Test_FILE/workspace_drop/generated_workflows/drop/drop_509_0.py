# Workflow ID: drop_509_0
# Benchmark: drop
# Data Indices: [1417, 1175, 3707, 355]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract all touchdown plays from the passage and identify their yardage.</instruction>
    <input>1</input>
    <output>touchdowns</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter touchdowns that were 5 yards or less in length.</instruction>
    <input>2</input>
    <output>short_touchdowns</output>
  </node>
  <node id="4" type="agent">
    <instruction>Count the number of filtered short touchdowns.</instruction>
    <input>3</input>
    <output>count</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <parameter>final_answer</parameter>
  </node>