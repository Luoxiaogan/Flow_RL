# Workflow ID: drop_520_0
# Benchmark: drop
# Data Indices: [1409, 1980, 2481, 1496]

<start>
    <task>Extract relevant numerical data from the passage</task>
    <next>agent1</next>
  </start>

  <agent1>
    <instruction>Identify all numeric values related to the question and their context. Focus on exact matches for the required comparison or calculation.</instruction>
    <output>numerical_data</output>
    <next>agent2</next>
  </agent1>

  <agent2>
    <instruction>From the extracted numerical data, determine which values are directly relevant to answering the question. Discard any irrelevant numbers.</instruction>
    <output>filtered_data</output>
    <next>agent3</next>
  </agent2>

  <agent3>
    <instruction>Perform the required arithmetic operation (e.g., subtraction, comparison) using the filtered data to derive the answer.</instruction>
    <output>result</output>
    <next>final</next>
  </agent3>

  <final>
    <task>Return the final computed result as the answer to the question.</task>
    <output>final_answer</output>
  </final>