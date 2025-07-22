# Workflow ID: hotpotqa_229_0
# Benchmark: hotpotqa
# Data Indices: [3601, 484, 3844, 3875]

<operator id="1">
    <instruction>Identify the key elements in the question and determine what information is needed to answer it.</instruction>
    <input>problem</input>
    <output>question_analysis</output>
  </operator>

  <operator id="2">
    <instruction>Extract relevant mountain elevation data from the context provided, focusing on Kangchenjunga and Passu Sar.</instruction>
    <input>context</input>
    <output>mountain_data</output>
  </operator>

  <operator id="3">
    <instruction>Compare the elevations of Kangchenjunga and Passu Sar to determine which is higher.</instruction>
    <input>mountain_data</input>
    <output>elevation_comparison</output>
  </operator>

  <operator id="4">
    <instruction>Determine if the third-highest mountain in the world is among the two compared. Use known global rankings to verify.</instruction>
    <input>elevation_comparison</input>
    <output>ranking_verification</output>
  </operator>

  <operator id="5">
    <instruction>Based on the verification, return the correct answer: either Kangchenjunga or Passu Sar as the third highest mountain.</instruction>
    <input>ranking_verification</input>
    <output>final_answer</output>
  </operator>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>