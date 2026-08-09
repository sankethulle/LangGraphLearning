from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated 
from pydantic import BaseModel,Field
from dotenv import load_dotenv
import operator

load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini"
)
class UpscState(TypedDict):
    eassy:str
    language_feedback:str
    analysis_feedback:str
    clarity_feedback:str
    overall_feedback:str
    indivisual_score:Annotated[list[int],operator.add]
    avg_score:int

class EvaluationSchema(BaseModel):
    feedback:str=Field(description="Detailed feedback for easy")   
    score:int=Field(description="Score out of 10",gt=0,le=10)
     
structuredllm = llm.with_structured_output(EvaluationSchema)

def performAnalysisFeedback(state:UpscState)->dict:
    print(f'In [performAnalysisFeedback]')    
    prompt  = f""" 
                perform analusis and return feedback, score based on analysis for defined easy:
                {state['eassy']}    
                """
    response = structuredllm.invoke(prompt)
    return {
        'analysis_feedback':response.feedback,
        'indivisual_score':[response.score]
    }
def performclarityFeedback(state:UpscState)->dict:  
    print(f'In [performclarityFeedback]')     
    prompt  = f""" 
                perform tone clarity check and return feedback, score based on clarity check for defined easy:
                {state['eassy']}    
                """     
    response = structuredllm.invoke(prompt)
    return {
        'clarity_feedback':response.feedback,
        'indivisual_score':[response.score]
    }

def performLanguageFeedback(state:UpscState)->dict:
    print(f'In [performLanguageFeedback]')         
    prompt  = f""" 
                    perform langauage check and return feedback, score based on language check check for defined easy:
                    {state['eassy']}    
                    """     
    response = structuredllm.invoke(prompt)
    return {
            'language_feedback':response.feedback,
            'indivisual_score':[response.score]
    }
        

def overall_feedback(state:UpscState)->dict: 
    print(f'In [overall_feedback]')            
    prompt  = f""" 
                perform check against all feedback returned from each 
                analysis,clarity and language check and return
                overall summarized feedback:
                language feedback{state['language_feedback']}    
                clarity feedback{state['clarity_feedback']}   
                Analysis feedback{state['analysis_feedback']}   
                """
    response = llm.invoke(prompt)
    json_response = getattr(response, "content", None) or response     
    
    return {
        'overall_feedback':json_response,
        'avg_score':round(sum(state['indivisual_score'])/len(state['indivisual_score']),2)     
    }

graph = StateGraph(UpscState)
graph.add_node("performAnalysisFeedback",performAnalysisFeedback)
graph.add_node("performclarityFeedback",performclarityFeedback)
graph.add_node("performLanguageFeedback",performLanguageFeedback)
graph.add_node("overall_feedback",overall_feedback)

# Fan OUT
graph.add_edge(START,"performAnalysisFeedback")
graph.add_edge(START,"performclarityFeedback")
graph.add_edge(START,"performLanguageFeedback")

# Fan IN
graph.add_edge("performAnalysisFeedback","overall_feedback")
graph.add_edge("performclarityFeedback","overall_feedback")
graph.add_edge("performLanguageFeedback","overall_feedback")

graph.add_edge("overall_feedback",END)

workflow = graph.compile()
# Good easy
# sample_easy = f"""
# Artificial Intelligence (AI) is becoming an important part of everyday life in India. AI means using computers and software that can learn from information and perform tasks that normally need human intelligence. Today, AI is being used in many areas such as education, healthcare, banking, agriculture, transportation, and customer service.

# In education, AI can help students learn through personalized lessons, practice questions, and smart learning applications. Teachers can also use AI to prepare study materials and understand where students need more help. In healthcare, AI can support doctors by analyzing medical reports and helping identify diseases at an early stage.

# Indian banks and financial companies use AI to detect unusual transactions and reduce online fraud. In agriculture, AI can help farmers understand weather conditions, identify crop diseases, and improve the use of water and fertilizers. AI is also being used in cars, traffic management, factories, and online shopping.

# India has a large technology workforce and a growing startup ecosystem, which creates good opportunities for AI development. The government and private companies are also investing in AI research and digital infrastructure.

# However, AI also brings challenges. People need to think about data privacy, security, incorrect information, job changes, and responsible use of AI. AI should be used as a tool to support people rather than completely replace human judgment.

# With proper rules, education, and responsible development, AI can help India improve productivity, create new opportunities, and provide better services to people.
# """
# Bad easy
sample_easy=f"""
AI in India is growing very fast. AI means Artificial Intelligence. It helps computers do some work like humans. Many people in India use AI every day, sometimes without knowing it.

AI is used in mobile phones, Google search, online shopping, banks, hospitals and schools. For example, when we use Google Maps, AI helps us find the best route. In shopping apps, AI can show products that we may like.

AI can also help farmers. It can give information about weather and crops. In hospitals, AI can help doctors check some reports. Students can use AI to learn new things and get help with their studies.

AI is useful, but it can also have some problems. Sometimes AI gives wrong answers. People should not believe everything given by AI. We should check important information before using it.

India has many IT companies and skilled people, so AI can grow more in the future. AI can create new jobs and also change some old jobs.

I think AI is a useful technology. We should learn how to use it properly and safely. AI can help India grow and make many things easier for people."""
input_state = {'eassy':sample_easy}
print(workflow.invoke(input_state))
