# from langchain.chat_models.gigachat import GigaChat
from langchain_community.chat_models.gigachat import GigaChat
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage
import base64
from llm.model.auth_data import client_secret, client_id
from utils.preprocessing_data import txt_to_str


class GiGaChatBot:
    def __init__(self):
        self.client_secret = client_secret
        self.client_id = client_id
        self.giga_api = None
        self.llm = None
        self.conversation = None
        self.message = None

    def get_giga_api(self):
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        self.giga_api = encoded_credentials

    def create_giga_model(self):
        self.get_giga_api()
        llm = GigaChat(
            credentials=self.giga_api,
            verify_ssl_certs=False
        )
        conversation = ConversationChain(
            llm=llm,
            verbose=False,
            memory=ConversationBufferMemory(llm=llm)
        )

        self.llm = llm
        self.conversation = conversation

    def add_prompt(self, file_path):
        template = txt_to_str(file_path=file_path)
        self.conversation.prompt.template = template

    def giga_answer(self, user_text):
        return self.conversation.predict(input=user_text)

    def add_system_message(self, system_message):
        self.message = [
            SystemMessage(
                content=system_message
            )
        ]

    def giga_dialog(self, user_message):
        self.message.append(HumanMessage(content=user_message))
        answer = self.llm(self.message)
        self.message.append(answer)

        return answer.content

