# Workflow ID: drop_556_0
# Benchmark: drop
# Data Indices: [3680, 926, 3787, 1560, 3396]

<node id="1" type="input">
        <param name="problem" type="string"/>
    </node>
    
    <node id="2" type="agent">
        <instruction>
            Analyze the problem step by step. Identify key numerical data or relationships. If a question asks for a count, percentage, or specific value, extract it directly from the passage. Do not generate multiple answers unless explicitly asked.
        </instruction>
        <input>problem</input>
        <output>parsed_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>
            For each question, determine if the required information is explicitly stated or can be derived from the passage. If yes, return the exact answer. If no, return "Not specified".
        </instruction>
        <input>parsed_data</input>
        <output>answer</output>
    </node>
    
    <node id="4" type="output">
        <input>answer</input>
    </node>