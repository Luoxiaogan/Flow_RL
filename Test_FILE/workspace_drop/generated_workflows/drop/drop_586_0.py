# Workflow ID: drop_586_0
# Benchmark: drop
# Data Indices: [3549, 3799, 3870, 1345]

<agent id="1">
    <instruction>Identify the first scoring play in the game by analyzing the chronological order of events described in the passage.</instruction>
    <output>First score: Field goal by [Player Name] for [Team Name].</output>
  </agent>
  <agent id="2">
    <instruction>Determine which player scored the first touchdown by locating the earliest touchdown event in the passage.</instruction>
    <output>First touchdown scorer: [Player Name] with a [Yardage]-yard TD.</output>
  </agent>
  <agent id="3">
    <instruction>Extract all field goals from the passage and find the shortest one by comparing yardages.</instruction>
    <output>Shortest field goal: [Yardage]-yard field goal by [Player Name].</output>
  </agent>
  <agent id="4">
    <instruction>Find the longest field goal by scanning through all field goal mentions in the passage and comparing distances.</instruction>
    <output>Longest field goal: [Yardage]-yard field goal by [Player Name].</output>
  </agent>
  <agent id="5">
    <instruction>Summarize the sequence of scoring plays to determine who scored first overall (field goal or touchdown).</instruction>
    <output>First score in the game: [Type] by [Player Name] for [Team Name].</output>
  </agent>
  <connection>
    <from>1</from>
    <to>5</to>
  </connection>
  <connection>
    <from>2</from>
    <to>5</to>
  </connection>
  <connection>
    <from>3</from>
    <to>5</to>
  </connection>
  <connection>
    <from>4</from>
    <to>5</to>
  </connection>