# Workflow ID: drop_787_0
# Benchmark: drop
# Data Indices: [2209, 160, 180, 1876]

<agent id="1">
    <instruction>Extract all field goal and touchdown values from the passage.</instruction>
    <output>list_of_plays</output>
  </agent>
  
  <agent id="2">
    <instruction>Filter only touchdowns and identify those under the specified yard threshold.</instruction>
    <input>list_of_plays</input>
    <output>short_touchdowns</output>
  </agent>
  
  <agent id="3">
    <instruction>Count how many of these touchdowns are under the threshold.</instruction>
    <input>short_touchdowns</input>
    <output>count</output>
  </agent>
  
  <agent id="4">
    <instruction>Identify field goals made by a specific kicker mentioned in the question.</instruction>
    <input>list_of_plays</input>
    <output>kicker_field_goals</output>
  </agent>
  
  <agent id="5">
    <instruction>Calculate the difference between the second and first field goal of that kicker.</instruction>
    <input>kicker_field_goals</input>
    <output>difference</output>
  </agent>
  
  <agent id="6">
    <instruction>Determine which plays were scored by a particular player (e.g., Quinn Gray).</instruction>
    <input>list_of_plays</input>
    <output>player_plays</output>
  </agent>
  
  <agent id="7">
    <instruction>Compute the yardage difference between the second and first play of that player.</instruction>
    <input>player_plays</input>
    <output>yardage_diff</output>
  </agent>
  
  <agent id="8">
    <instruction>Aggregate all results: count of short touchdowns, field goal difference, and player yardage difference.</instruction>
    <input>count, difference, yardage_diff</input>
    <output>final_answer</output>
  </agent>