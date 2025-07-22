# Workflow ID: drop_668_0
# Benchmark: drop
# Data Indices: [3103, 2754, 1064, 3431]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract all touchdown pass plays from the passage, noting the quarterback and receiver details.</instruction>
    <input>1</input>
    <output>passes</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify all field goal distances mentioned in the passage and store them as a list of integers.</instruction>
    <input>1</input>
    <output>field_goals</output>
  </node>
  <node id="4" type="agent">
    <instruction>From the extracted touchdown passes, determine the longest pass by comparing yardage values.</instruction>
    <input>2</input>
    <output>longest_pass_yards</output>
  </node>
  <node id="5" type="agent">
    <instruction>From the extracted field goals, find the maximum distance among them.</instruction>
    <input>3</input>
    <output>longest_field_goal</output>
  </node>
  <node id="6" type="agent">
    <instruction>Determine which team scored the most in the first half by analyzing scoring events before halftime.</instruction>
    <input>1</input>
    <output>first_half_winner</output>
  </node>
  <node id="7" type="agent">
    <instruction>Find the kicker who made a 40-yard field goal by matching the exact yardage in the field goal list.</instruction>
    <input>3</input>
    <output>kicker_40_yard</output>
  </node>
  <node id="8" type="output">
    <input>4</input>
    <input>5</input>
    <input>6</input>
    <input>7</input>
    <output>final_answer</output>
  </node>