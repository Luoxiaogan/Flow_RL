# Workflow ID: drop_408_0
# Benchmark: drop
# Data Indices: [2770, 1680, 1051, 560]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract the relevant information from the passage related to the question. Identify key events, scores, and team performance metrics that directly address the query.</instruction>
        <input>1</input>
    </node>
    
    <node id="3" type="agent">
        <instruction>Perform step-by-step reasoning based on the extracted information. Calculate or determine the exact value needed to answer the question using logical deductions and numerical operations if necessary.</instruction>
        <input>2</input>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify the calculation or logic used in the previous step. Cross-check with other parts of the passage to ensure consistency and correctness of the derived answer.</instruction>
        <input>3</input>
    </node>
    
    <node id="5" type="output">
        <instruction>Return the final answer based on verified reasoning. Ensure it is concise, accurate, and directly addresses the original question.</instruction>
        <input>4</input>
    </node>