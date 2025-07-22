# Workflow ID: drop_518_0
# Benchmark: drop
# Data Indices: [3170, 2767, 557, 3733]

<agent id="1">
    <instruction>Identify the relevant numerical data from the passage related to the question.</instruction>
    <output>Extract all yardage values mentioned in the passage that pertain to the question asked.</output>
  </agent>
  <agent id="2">
    <instruction>Process the extracted data to isolate the specific values needed for comparison or calculation.</instruction>
    <output>Filter and organize the values into groups based on their relevance to the question (e.g., first TD pass, third TD pass).</output>
  </agent>
  <agent id="3">
    <instruction>Perform the required mathematical operation (e.g., subtraction, comparison) on the processed values.</instruction>
    <output>Calculate the difference between the specified values (e.g., first vs. third touchdown pass yards).</output>
  </agent>
  <agent id="4">
    <instruction>Determine if any additional context (like multiple touchdowns by a player) is needed to answer the question fully.</instruction>
    <output>Check for players who scored more than once and extract their respective yardages if applicable.</output>
  </agent>
  <agent id="5">
    <instruction>Validate the final result against the original question to ensure correctness.</instruction>
    <output>Confirm the calculated value matches the exact requirement of the question (e.g., "difference in yards").</output>
  </agent>
  <agent id="6">
    <instruction>Format the output as a single integer or float depending on the nature of the question.</instruction>
    <output>Return the final numeric answer as an integer.</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="2" to="4"/>
  <connection from="3" to="5"/>
  <connection from="4" to="5"/>
  <connection from="5" to="6"/>