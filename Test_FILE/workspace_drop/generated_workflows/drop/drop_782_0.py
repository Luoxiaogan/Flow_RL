# Workflow ID: drop_782_0
# Benchmark: drop
# Data Indices: [3997, 51, 2879, 737]

<agent id="1">
    <instruction>Identify all field goals in the passage and extract their yardages.</instruction>
    <output>list of field goal yardages</output>
  </agent>
  <agent id="2">
    <instruction>Filter the field goals to include only those between 30 and 40 yards.</instruction>
    <input>list of field goal yardages from agent 1</input>
    <output>filtered list of field goals between 30 and 40 yards</output>
  </agent>
  <agent id="3">
    <instruction>Count the number of field goals in the filtered list.</instruction>
    <input>filtered list from agent 2</input>
    <output>integer count of field goals between 30 and 40 yards</output>
  </agent>
  <connect>
    <from>1</from>
    <to>2</to>
  </connect>
  <connect>
    <from>2</from>
    <to>3</to>
  </connect>