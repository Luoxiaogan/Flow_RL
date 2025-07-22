# Workflow ID: hotpotqa_83_0
# Benchmark: hotpotqa
# Data Indices: [3159, 3703, 888, 3772, 2262]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the problem. Extract relevant information from the context that directly answers the question.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Compare the extracted information to determine which entity meets the criteria specified in the question (e.g., birth date, award category, etc.).</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Validate the comparison result by cross-referencing with any additional context that might clarify ambiguity or confirm correctness.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="output">
        <instruction>Return the final answer based on the validated result from the previous step.</instruction>
        <input>4</input>
    </node>