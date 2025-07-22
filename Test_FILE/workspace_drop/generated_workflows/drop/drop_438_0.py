# Workflow ID: drop_438_0
# Benchmark: drop
# Data Indices: [1108, 2416, 1590, 2529, 3088]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the passage to identify all touchdown runs and their distances. Focus only on the TD runs mentioned in the text.
        </instruction>
        <input>problem</input>
        <output>td_runs</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            From the list of touchdown runs, determine the shortest one by comparing the yardage values step by step.
        </instruction>
        <input>td_runs</input>
        <output>shortest_td_run</output>
    </node>
    
    <node id="4" type="output">
        <param name="result" />
    </node>
    
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />