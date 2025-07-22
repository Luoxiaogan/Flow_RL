# Workflow ID: drop_674_0
# Benchmark: drop
# Data Indices: [3348, 1002, 3228, 2499]

<node id="1" type="input">
        <param name="problem">self.problem</param>
    </node>
    
    <node id="2" type="agent">
        <instruction>Extract relevant numerical data from the passage that answers the question. Focus on key values such as scores, yardages, or counts mentioned in relation to the question.</instruction>
        <param name="input">1</param>
        <output>extracted_data</output>
    </node>
    
    <node id="3" type="agent">
        <instruction>Identify the specific event or metric being asked for (e.g., touchdowns, field goals, percentages). Use logical reasoning to determine which extracted value directly answers the question.</instruction>
        <param name="input">2</param>
        <output>reasoned_answer</output>
    </node>
    
    <node id="4" type="agent">
        <instruction>Verify the correctness of the reasoned answer by cross-checking with the passage. Ensure no misinterpretation occurred and that the answer is consistent with the context.</instruction>
        <param name="input">3</param>
        <output>verified_answer</output>
    </node>
    
    <node id="5" type="output">
        <param name="answer">4</param>
        <param name="input">4</param>
    </node>