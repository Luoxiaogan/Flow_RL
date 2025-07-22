# Workflow ID: hotpotqa_425_0
# Benchmark: hotpotqa
# Data Indices: [3591, 2355, 3640, 1476, 2534]

<start>
    <operator name="extract_relevant_info">
      <instruction>Identify the key entities and relationships in the context that relate to the question. Focus on the school and its location.</instruction>
    </operator>
  </start>

  <operator name="locate_university">
    <instruction>From the extracted information, determine which university Keiki Kawaiʻaeʻa received her BA from. Ensure the answer is specific and accurate.</instruction>
  </operator>

  <operator name="identify_county">
    <instruction>Once the university is identified, find the county where this university is located based on geographic knowledge or contextual clues.</instruction>
  </operator>

  <operator name="validate_and_return">
    <instruction>Verify the correctness of the county by cross-referencing with known geographic facts about the university's location. Return only the final county name as the answer.</instruction>
  </operator>

  <end>