# Workflow ID: hotpotqa_252_0
# Benchmark: hotpotqa
# Data Indices: [3146, 3784, 592, 3953, 1230]

<agent id="1">
    <instruction>Identify the key elements in the problem statement that relate to the question.</instruction>
    <output>Extract relevant entities and facts from the context provided.</output>
  </agent>
  <agent id="2">
    <instruction>Map the extracted entities to known data points or categories in the context.</instruction>
    <output>Establish connections between the entities (e.g., town, year founded, incorporation date).</output>
  </agent>
  <agent id="3">
    <instruction>Verify the consistency of the mapped data with the question's requirements.</instruction>
    <output>Determine if the town's founding year matches the given condition and find its incorporation date.</output>
  </agent>
  <agent id="4">
    <instruction>Validate the final answer against all contextual clues to ensure accuracy.</instruction>
    <output>Return the correct incorporation year based on verified data.</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>