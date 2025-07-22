# Workflow ID: hotpotqa_334_0
# Benchmark: hotpotqa
# Data Indices: [159, 34, 3340, 1105]

<operator id="0" type="agent">
        <instruction>Think step by step to identify the genus that honors John Parkinson based on botanical references in the context.</instruction>
        <input>context</input>
        <output>genus_candidate</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>Verify which genus, Parkinsonia or Rumohra, is explicitly stated to honor John Parkinson in the provided context.</instruction>
        <input>genus_candidate</input>
        <output>verification_result</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Check if the context mentions any other John Parkinson (e.g., cardiologist, steward) that might be confused with the botanist.</instruction>
        <input>context</input>
        <output>conflict_check</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Based on all prior results, determine the correct genus honoring the botanist John Parkinson.</instruction>
        <input>verification_result, conflict_check</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="2" to="3"/>
    <edge from="1" to="3"/>