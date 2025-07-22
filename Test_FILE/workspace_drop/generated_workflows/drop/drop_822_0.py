# Workflow ID: drop_822_0
# Benchmark: drop
# Data Indices: [261, 168, 605, 279]

<agent id="1">
    <instruction>Identify the key information in the passage related to the question. Focus on specific details like names, scores, and events that directly answer the question.</instruction>
    <output>Extract relevant data points from the passage that pertain to the question asked.</output>
  </agent>
  <agent id="2">
    <instruction>Process the extracted data to determine the exact values or facts needed to answer the question. If multiple pieces of data exist, prioritize those that are most directly relevant.</instruction>
    <output>Refine the extracted data into a clear, precise answer based on the question's requirements.</output>
  </agent>
  <agent id="3">
    <instruction>Validate the refined answer against the original passage to ensure accuracy and completeness. Check for any inconsistencies or missing elements.</instruction>
    <output>Confirm that the answer is correct and fully supported by the passage.</output>
  </agent>
  <agent id="4">
    <instruction>Format the final answer according to the expected output structure—this may include numerical values, named entities, or concise statements.</instruction>
    <output>Provide the correctly formatted final answer to the question.</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>