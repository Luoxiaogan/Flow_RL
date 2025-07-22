# Workflow ID: drop_259_0
# Benchmark: drop
# Data Indices: [1617, 1135, 536, 2579]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the passage to identify all relevant numerical data related to the question. Extract exact values and context for each key event.
        </instruction>
        <input>problem</input>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            For Problem 1: Identify all touchdown distances and select the two shortest ones. Sum them.
            For Problem 2: Subtract the first field goal distance from the second.
            For Problem 3: Subtract the final score of the losing team from the winning team.
            For Problem 4: Calculate the duration between the start and end years of Mongol control.
        </instruction>
        <input>extracted_data</input>
        <output>solutions</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>
            Validate each solution by cross-checking with the original passage. Ensure no arithmetic or interpretation errors exist.
        </instruction>
        <input>solutions</input>
        <output>validated_solutions</output>
    </node>
    
    <node id="5" type="output">
        <input>validated_solutions</input>
        <output>final_answer</output>
    </node>