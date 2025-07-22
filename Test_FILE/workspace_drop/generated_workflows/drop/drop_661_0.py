# Workflow ID: drop_661_0
# Benchmark: drop
# Data Indices: [2402, 2462, 1769, 539, 2738]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract all instances of touchdowns from the passage. Classify each as either passing or rushing based on the description.</instruction>
    <input>1</input>
    <output>touchdowns_list</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter the list to count only passing touchdowns by checking if the description includes terms like 'TD pass', 'completed a TD pass', or similar phrasing.</instruction>
    <input>2</input>
    <output>passing_touchdowns_count</output>
  </node>
  <node id="4" type="output">
    <input>3</input>
    <param name="result">passing_touchdowns_count</param>
  </node>