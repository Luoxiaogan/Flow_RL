# Workflow ID: hotpotqa_302_0
# Benchmark: hotpotqa
# Data Indices: [1272, 1568, 2511, 1257]

<start/>
    <agent id="1" instruction="Identify the key entity in the question and locate its relevant context. Break down the question into core components: who, what, where, and when."/>
    <agent id="2" instruction="Extract explicit information from the context that directly answers the question. Focus only on facts that match the question's requirements without adding assumptions."/>
    <agent id="3" instruction="Verify the extracted answer against the broader context to ensure accuracy and avoid misinterpretation due to similar-sounding entities or names."/>
    <agent id="4" instruction="If multiple potential answers exist, use logical filtering based on temporal, geographic, or categorical constraints mentioned in the question to select the correct one."/>
    <agent id="5" instruction="Synthesize the verified information into a clear, concise final answer that directly addresses the original question."/>
    <end/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="end"/>