# Workflow ID: drop_497_0
# Benchmark: drop
# Data Indices: [997, 1191, 3530, 1474, 1829]

<node id="1" type="input">
    <prompt>Extract all scoring events from the passage, including players and types of scores (TD, FG).</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify each player who scored a touchdown. List them with the yardage if specified.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Identify each field goal kicker and the yardage of each field goal they made.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Determine which team won by comparing total points scored by each team.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="5" type="agent">
    <prompt>Count the total number of touchdowns scored in the game.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="6" type="combine">
    <prompt>Aggregate results from all agents: list of TD scorers, FG kickers with yardages, winner, and total TD count.</prompt>
    <depends_on>2,3,4,5</depends_on>
  </node>
  <node id="7" type="output">
    <prompt>Return structured output: {td_scorers, fg_kickers_with_yardages, winner, total_touchdowns}</prompt>
    <depends_on>6</depends_on>
  </node>