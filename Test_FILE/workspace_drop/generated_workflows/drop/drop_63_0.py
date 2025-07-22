# Workflow ID: drop_63_0
# Benchmark: drop
# Data Indices: [1155, 1228, 3785, 2679, 3611]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify key players, scores, and distances mentioned.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter out only the values that directly answer the question. For example, if the question asks for yardage of a specific play, isolate those numbers.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Compare each filtered value against the condition in the question (e.g., "longer than 50 yards"). Return a list of values that meet the criteria.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="agent">
    <instruction>Identify which players correspond to the qualifying plays. Map each qualifying yardage to the player who achieved it.</instruction>
    <input>4</input>
    <output>5</output>
  </node>
  <node id="6" type="agent">
    <instruction>Format the final output as a list of players who scored touchdowns longer than the specified threshold (e.g., 50 yards).</instruction>
    <input>5</input>
    <output>6</output>
  </node>
  <node id="7" type="output">
    <input>6</input>
  </node>