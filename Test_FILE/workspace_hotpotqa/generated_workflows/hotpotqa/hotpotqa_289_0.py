# Workflow ID: hotpotqa_289_0
# Benchmark: hotpotqa
# Data Indices: [421, 355, 2661, 3063, 315]

<node id="1" type="input">
        <param name="problem" />
    </node>
    
    <node id="2" type="agent">
        <instruction>Think step by step: Identify the key entities in the problem and determine what is being asked. Break down the question into components that can be matched with the context.</instruction>
        <input>1</input>
    </node>
    
    <node id="3" type="agent">
        <instruction>Extract relevant facts from the context for each entity mentioned in the question. Focus only on information that directly answers the query.</instruction>
        <input>2</input>
    </node>
    
    <node id="4" type="agent">
        <instruction>Compare the extracted facts to determine which option satisfies the condition in the question (e.g., more diverse career, more students, etc.). Ensure your reasoning aligns with the data provided.</instruction>
        <input>3</input>
    </node>
    
    <node id="5" type="output">
        <param name="answer" />
        <input>4</input>
    </node>