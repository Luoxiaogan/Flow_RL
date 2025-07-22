# Workflow ID: hotpotqa_67_0
# Benchmark: hotpotqa
# Data Indices: [1217, 566, 3528, 2264, 1396]

<node id="1" type="input">
        <data>problem</data>
    </node>
    <node id="2" type="agent">
        <instruction>Identify the key entities and relationships in the problem. Break down the question into its core components to determine what information is being sought.</instruction>
        <input>1</input>
    </node>
    <node id="3" type="agent">
        <instruction>Based on the context provided, locate any direct or indirect references that connect the key entities identified in the previous step. Focus on specific details like names, dates, or titles.</instruction>
        <input>2</input>
    </node>
    <node id="4" type="agent">
        <instruction>Verify if the connections found in the previous step lead to a definitive answer. If not, look for related concepts or additional context that might clarify the relationship between the entities.</instruction>
        <input>3</input>
    </node>
    <node id="5" type="agent">
        <instruction>Construct a logical pathway from the initial question to the final answer using the verified connections. Ensure each step builds upon the last without introducing ambiguity.</instruction>
        <input>4</input>
    </node>
    <node id="6" type="output">
        <instruction>Return the final answer based on the validated pathway. Do not include any intermediate reasoning or extra explanation unless explicitly requested.</instruction>
        <input>5</input>
    </node>