# Workflow ID: drop_682_0
# Benchmark: drop
# Data Indices: [2224, 3123, 3369, 896]

<agent id="1" type="extract">
    <instruction>Identify the key event or action from the passage that directly answers the question. Focus on specific scores, players, and their actions.</instruction>
  </agent>
  <agent id="2" type="filter">
    <instruction>From the extracted events, filter out only those relevant to the question asked—such as scoring plays, players involved, and their respective yardages or timing.</instruction>
  </agent>
  <agent id="3" type="aggregate">
    <instruction>Combine filtered results to determine the correct answer by comparing values (e.g., yardage, time, score) and identifying the unique match for the query.</instruction>
  </agent>
  <agent id="4" type="validate">
    <instruction>Verify the consistency of the answer with the passage: check if the player, play, or yardage matches any explicit mention in the text without introducing unsupported assumptions.</instruction>
  </agent>
  <agent id="5" type="format">
    <instruction>Structure the final output in a clear, concise format that directly answers the question using only the validated information.</instruction>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>