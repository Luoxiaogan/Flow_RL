# Workflow ID: drop_590_0
# Benchmark: drop
# Data Indices: [2682, 3561, 461, 309]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key elements in the passage relevant to the question. Focus on specific actions, players, and outcomes mentioned.</instruction>
        <input>1</input>
        <output>key_elements</output>
    </node>
    <node id="3" type="agent">
        <instruction>Extract numerical data or comparisons that directly answer the question. For example, compare field goal distances or touchdown scores.</instruction>
        <input>2</input>
        <output>extracted_data</output>
    </node>
    <node id="4" type="agent">
        <instruction>Determine the final answer by evaluating the extracted data against the question's requirements. Ensure only one correct answer is selected based on evidence.</instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    <node id="5" type="output">
        <input>4</input>
        <output>answer</output>
    </node>