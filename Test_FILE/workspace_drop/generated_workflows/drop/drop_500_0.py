# Workflow ID: drop_500_0
# Benchmark: drop
# Data Indices: [1006, 2463, 958, 1424]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage related to the question. Identify all values that could be used in calculations.</instruction>
        <input>1</input>
        <output>extracted_values</output>
    </node>
    <node id="3" type="agent">
        <instruction>Identify which values are directly needed for the answer based on the question's structure (e.g., percentages, counts, distances).</instruction>
        <input>2</input>
        <output>relevant_values</output>
    </node>
    <node id="4" type="agent">
        <instruction>Apply mathematical operations (e.g., subtraction, division, percentage difference) using the relevant values to compute the final answer.</instruction>
        <input>3</input>
        <output>computed_result</output>
    </node>
    <node id="5" type="agent">
        <instruction>Validate the result by checking if it logically fits the context of the question and matches expected units or format.</instruction>
        <input>4</input>
        <output>validated_result</output>
    </node>
    <node id="6" type="output">
        <input>5</input>
        <output>final_answer</output>
    </node>