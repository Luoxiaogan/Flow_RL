# Workflow ID: drop_815_0
# Benchmark: drop
# Data Indices: [2587, 3628, 2519, 2914]

<agent id="1">
    <instruction>Identify the key numerical data points related to the question from the passage.</instruction>
    <output>Extract relevant values (e.g., yardages, counts) mentioned in the passage that directly answer the question.</output>
  </agent>
  <agent id="2">
    <instruction>Filter and isolate only the values that pertain to the specific query being asked.</instruction>
    <output>Discard irrelevant information; retain only numbers or metrics tied to the question's focus (e.g., touchdowns, field goals, yards).</output>
  </agent>
  <agent id="3">
    <instruction>Perform arithmetic or logical operations based on the filtered values to derive the final answer.</instruction>
    <output>Calculate differences, totals, or comparisons as required by the question using the filtered values.</output>
  </agent>
  <agent id="4">
    <instruction>Verify the result by cross-referencing with the original passage to ensure accuracy.</instruction>
    <output>Confirm that the derived answer matches the context of the passage and no misinterpretation occurred.</output>
  </agent>
  <agent id="5">
    <instruction>Format the final output clearly and concisely for direct use.</instruction>
    <output>Return a single, well-formatted numeric or descriptive answer based on the verified result.</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>