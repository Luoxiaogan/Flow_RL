# Workflow ID: drop_475_0
# Benchmark: drop
# Data Indices: [2828, 2944, 3174, 618, 1253]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <description>Identify all TD passes in the passage and extract their yardages</description>
    <operator>extract_td_passes</operator>
  </node>
  <node id="3" type="agent">
    <description>Sum total yards for each team mentioned in the question</description>
    <operator>sum_team_yards</operator>
  </node>
  <node id="4" type="agent">
    <description>Compare totals to determine which team had more TD pass yards</description>
    <operator>compare_totals</operator>
  </node>
  <node id="5" type="output">
    <description>Return the team with more TD pass yards</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>