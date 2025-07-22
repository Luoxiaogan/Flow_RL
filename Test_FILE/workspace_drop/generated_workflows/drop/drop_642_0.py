# Workflow ID: drop_642_0
# Benchmark: drop
# Data Indices: [3775, 1638, 3345, 3101]

<agent id="1">
    <instruction>Identify all scoring plays in the passage and extract their yardage.</instruction>
    <output>list_of_plays</output>
  </agent>
  
  <agent id="2">
    <instruction>Filter the list to include only touchdowns with yardage less than 10 yards.</instruction>
    <input>list_of_plays</input>
    <output>short_touchdowns</output>
  </agent>
  
  <agent id="3">
    <instruction>Count the number of filtered short touchdowns.</instruction>
    <input>short_touchdowns</input>
    <output>count</output>
  </agent>
  
  <agent id="4">
    <instruction>Return the final count as the answer.</instruction>
    <input>count</input>
    <output>final_answer</output>
  </agent>