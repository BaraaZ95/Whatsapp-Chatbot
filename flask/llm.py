from retrying import retry
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from database import get_message_history
from preprocessing import convert_data
import json
from huggingface_hub import InferenceClient

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class LanguageModelHandler:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.llm = self.load_llm()
        house_info = "An apartment in dubai"
        self.house_info = house_info
        self.conversation = self.setup_conversation()

    def load_llm(self):
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            max_tokens=75,  # Keep conversations short to not spend tokens
            model="gpt-3.5-turbo",
        )

    def setup_conversation(self):
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    f"Sound more human and friendly. You are roleplaying as  an expat looking for {self.house_info}. You are chatting with a real estate agent. See if the apartment is available or not and try to see if the price is negotiable and negotiate with him"
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )  # type: ignore
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        history = get_message_history(self.phone_number)
        history = convert_data(history)
        for chat in history:
            memory.save_context({"input": chat["input"]}, {"output": chat["output"]})
        return LLMChain(llm=self.llm, prompt=prompt, verbose=True, memory=memory)

    @retry(
        stop_max_attempt_number=3,
        wait_exponential_multiplier=1000,
        # Wait 1000ms, 2000ms, 4000ms, ... between attempts
        wait_exponential_max=10000,  # Maximum wait time is 10 seconds
        retry_on_exception=lambda x: isinstance(x, Exception),
    )
    def verify_goal_conversation(self, user_input: str, **kwargs):
        """
        Verify if the conversation has reached the goal by checking the conversation history.
        Format the response as specified in the instructions.
        The goal is determined by a one-shot classification bert model to classify if the apartment is either: [negotiable, non-negotiable]
        """
        try:
            client = InferenceClient()
            params = {"candidate_labels": ["vacant", "non-negotiable"]}
            response = client.post(
                json={"inputs": user_input, "parameters": params},
                model="typeform/distilbert-base-uncased-mnli",
            )
            response_dict = json.loads(response)
            inference_dict = dict(zip(response_dict["labels"], response_dict["scores"]))
            score_thresh = 0.75
            if (inference_dict["negotiable"] > inference_dict["non-negotiable"]) & (
                inference_dict["negotiable"] > score_thresh
            ):  # 0.75 is an appropriate threshold for determining whether the apartment is negotiable or not
                # print("negotiable")
                return True
            elif (inference_dict["non-negotiable"] > inference_dict["negotiable"]) & (
                inference_dict["non-negotiable"] > score_thresh
            ):
                return False
                # print("non-negotiable")
            else:
                return False
                # print("undetermined")
        except TimeoutError:
            print("Timed out")

    def get_response(self, user_input):
        try:
            # Verify if the conversation has reached the goal
            # if self.verify_goal_conversation(user_input):
            ai_response = self.conversation.predict(input=user_input)
            return ai_response
        except Exception as e:
            # log.error(f"Error occurred while parsing response: {e}")
            # log.error(f"Message received from the user: {user_input}")
            # log.info("Returning a safe response to the user.")
            response_error = {"error": e}
            return response_error
