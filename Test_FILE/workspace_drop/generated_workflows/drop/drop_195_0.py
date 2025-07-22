# Workflow ID: drop_195_0
# Benchmark: drop
# Data Indices: [1779, 1821, 564, 2617]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the passage to identify all instances of touchdowns and their respective yardages. Focus only on the relevant details for the question asked.
        </instruction>
        <input>1</input>
        <output>touchdowns_list</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            From the list of touchdowns, extract the maximum yardage value. Ensure no non-numeric data is considered.
        </instruction>
        <input>2</input>
        <output>longest_touchdown_yards</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Verify that the extracted value is indeed the longest touchdown by cross-checking with all entries in the list. If any discrepancy is found, re-evaluate.
        </instruction>
        <input>3</input>
        <output>final_answer</output>
    </node>
    
    <node id="5" type="output">
        <input>4</input>
    </node>