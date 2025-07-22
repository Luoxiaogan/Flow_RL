# Workflow ID: drop_77_0
# Benchmark: drop
# Data Indices: [1375, 2947, 3584, 1898, 2564]

<operator id="0">
    <instruction>Identify all scoring plays in the given passage and extract their distances.</instruction>
    <input>problem</input>
    <output>scoring_plays</output>
  </operator>
  <operator id="1">
    <instruction>Filter for touchdown passes that are 20 yards or longer from the extracted scoring plays.</instruction>
    <input>scoring_plays</input>
    <output>long_touchdown_passes</output>
  </operator>
  <operator id="2">
    <instruction>Count the number of qualifying touchdown passes.</instruction>
    <input>long_touchdown_passes</input>
    <output>count</output>
  </operator>
  <operator id="3">
    <instruction>Return the final count as the answer to the question.</instruction>
    <input>count</input>
    <output>final_answer</output>
  </operator>