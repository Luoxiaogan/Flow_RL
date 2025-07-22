# Workflow ID: drop_634_0
# Benchmark: drop
# Data Indices: [1683, 3432, 3139, 379, 3175]

<agent id="1">
    <instruction>Identify all touchdown passes mentioned in the passage and their respective quarterbacks.</instruction>
    <output>list of (quarterback, yardage) tuples for each touchdown pass</output>
  </agent>
  <agent id="2">
    <instruction>Filter the list from Agent 1 to only include entries where the quarterback is Ben Roethlisberger.</instruction>
    <output>list of (yardage) for Ben Roethlisberger's touchdown passes</output>
  </agent>
  <agent id="3">
    <instruction>Sum all the yardages from Agent 2's output to compute total yards thrown by Ben Roethlisberger on touchdown passes.</instruction>
    <output>total_yards</output>
  </agent>
  <connection>
    <from>1</from>
    <to>2</to>
  </connection>
  <connection>
    <from>2</from>
    <to>3</to>
  </connection>