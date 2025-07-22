# Workflow ID: drop_513_0
# Benchmark: drop
# Data Indices: [2608, 1918, 3059, 26]

<node id="1">
    <operator>extract_field_values</operator>
    <input>problem</input>
    <output>field_goals, rushing_touchdowns, passing_touchdowns</output>
  </node>
  <node id="2">
    <operator>find_shortest</operator>
    <input>field_goals</input>
    <output>shortest_field_goal</output>
  </node>
  <node id="3">
    <operator>find_shortest</operator>
    <input>rushing_touchdowns</input>
    <output>shortest_rushing_td</output>
  </node>
  <node id="4">
    <operator>find_shortest</operator>
    <input>passing_touchdowns</input>
    <output>shortest_passing_td</output>
  </node>
  <node id="5">
    <operator>calculate_difference</operator>
    <input>passing_touchdowns, rushing_touchdowns</input>
    <output>total_passing_yards, total_rushing_yards</output>
  </node>
  <node id="6">
    <operator>compute_net_difference</operator>
    <input>total_passing_yards, total_rushing_yards</input>
    <output>difference</output>
  </node>
  <node id="7">
    <operator>merge_results</operator>
    <input>shortest_field_goal, shortest_rushing_td, shortest_passing_td, difference</input>
    <output>final_answer</output>
  </node>