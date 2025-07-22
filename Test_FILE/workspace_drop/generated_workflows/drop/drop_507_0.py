# Workflow ID: drop_507_0
# Benchmark: drop
# Data Indices: [3015, 3133, 506, 1196, 3214]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the relevant information in the passage related to Matt Stover's field goals in the first half.</instruction>
    <input>1</input>
    <output>stover_first_half_info</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract the yardages of all field goals Matt Stover made in the first half from the identified information.</instruction>
    <input>2</input>
    <output>stover_yardages</output>
  </node>
  <node id="4" type="agent">
    <instruction>Sum the yardages of Matt Stover's field goals from the first half to compute the total yards.</instruction>
    <input>3</input>
    <output>total_yards</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>