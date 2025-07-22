# Workflow ID: hotpotqa_52_0
# Benchmark: hotpotqa
# Data Indices: [2892, 1353, 3968, 3503]

<node id="1" type="question_analysis">
        <input>problem</input>
        <output>extracted_question, context_info</output>
        <instruction>Identify the core question and relevant context from the input problem.</instruction>
    </node>
    
    <node id="2" type="context_processing">
        <input>context_info</input>
        <output>structured_context</output>
        <instruction>Parse and structure the context into key entities, relationships, and facts for reasoning.</instruction>
    </node>
    
    <node id="3" type="agent_reasoning">
        <input>structured_context</input>
        <output>intermediate_answer</output>
        <instruction>Use logical deduction to connect entities in the context to answer the question step-by-step.</instruction>
    </node>
    
    <node id="4" type="verification">
        <input>intermediate_answer</input>
        <output>final_answer</output>
        <instruction>Validate the intermediate answer against the original question and context to ensure correctness.</instruction>
    </node>
    
    <node id="5" type="output_formatter">
        <input>final_answer</input>
        <output>formatted_output</output>
        <instruction>Format the final answer as a clear, concise response suitable for the user.</instruction>
    </node>
    
    <edge from="1" to="2" />
    <edge from="2" to="3" />
    <edge from="3" to="4" />
    <edge from="4" to="5" />