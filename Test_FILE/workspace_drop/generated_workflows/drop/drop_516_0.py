# Workflow ID: drop_516_0
# Benchmark: drop
# Data Indices: [704, 3235, 3023, 2875, 3810]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key elements in the passage relevant to the question. Focus on scoring events, players, and teams involved.</instruction>
    <input>problem</input>
    <output>parsed_events</output>
  </node>
  <node id="3" type="agent">
    <instruction>Extract all touchdowns and field goals from the parsed events. Categorize them by player and yardage.</instruction>
    <input>parsed_events</input>
    <output>scoring_summary</output>
  </node>
  <node id="4" type="agent">
    <instruction>From the scoring summary, identify the longest touchdown and the longest field goal. Calculate the difference in yards.</instruction>
    <input>scoring_summary</input>
    <output>yard_difference</output>
  </node>
  <node id="5" type="agent">
    <instruction>Determine the final answer based on the yard difference. Ensure it matches the exact question format.</instruction>
    <input>yard_difference</input>
    <output>final_answer</output>
  </node>
  <node id="6" type="output">
    <param>final_answer</param>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>