import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List
import random
from itertools import permutations
from ..utils.utils import llm_call

# Use python-dotenv to read .env file
from dotenv import load_dotenv
from openai import OpenAI
import networkx as nx

load_dotenv()
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url)

class BaseMessage:
    """
    Represents a message in the broadcast system.
    """

    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        content: List[Dict[str, str]],
        contribution_metric: float = 0.0,
    ):
        """
        Initialize a new Message.

        :param sender: The ID of the sender.
        :param receiver: The ID of the receiver.
        :param message_type: The type of message (e.g., "global_event", "local_event").
        :param content: The content of the message.
        """
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.timestamp = datetime.now().isoformat()

    def to_json(self):
        """
        Serialize the message to a JSON string.

        :return: A JSON string representing the message.
        """
        return json.dumps(
            {
                "sender": self.sender,
                "receiver": self.receiver,
                "message_type": self.message_type,
                "content": self.content,
                "timestamp": self.timestamp,
            },
            indent=4,
        )

    @classmethod
    def from_json(cls, json_str: str):
        """
        Deserialize a JSON string into a Message object.

        :param json_str: A JSON string representing the message.
        :return: A Message object.
        """
        if isinstance(json_str, str):
            data = json.loads(json_str)
        else:
            data = json_str
        return cls(
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=data["message_type"],
            content=data["content"],
        )

    def __repr__(self):
        """
        Return a string representation of the message.
        """
        return (
            f"Message(sender={self.sender}, receiver={self.receiver}, "
            f"message_type={self.message_type}, content={self.content}, "
            f"timestamp={self.timestamp})"
        )


class BaseConversation:
    """
    Represents a conversation owned by a single agent.
    """

    def __init__(self, owner_id: str, conversation_id: str, messages: List[BaseMessage]):
        """
        Initialize a new Conversation.

        :param conversation_id: The ID of the conversation.
        :param messages: A list of messages in the conversation.
        """
        self.conversation_id = conversation_id
        self.messages = messages
        self.owner = str(owner_id)

    def to_json(self):
        """
        Serialize the conversation to a JSON string.

        :return: A JSON string representing the conversation.
        """
        return json.dumps(
            {
                "conversation_id": self.conversation_id,
                "messages": [
                    json.loads(message.to_json()) for message in self.messages
                ],
            },
            indent=4,
        )

    @classmethod
    def from_json(cls, json_str: str):
        """
        Deserialize a JSON string into a Conversation object.

        :param json_str: A JSON string representing the conversation.
        :return: A Conversation object.
        """
        data = json.loads(json_str)
        messages = [BaseMessage.from_json(message)
                    for message in data["messages"]]
        return cls(conversation_id=data["conversation_id"], messages=messages)

    def add_message(self, message: BaseMessage):
        """
        Add a message to the conversation.

        :param message: The message to add to the conversation.
        """
        self.messages.append(message)

    def call_api(self, prompt: str, model="deepseek-chat", parameters: dict = None) -> str:
        """
        Calls the API and returns the system's response.

        :param prompt: The text sent to the API.
        :param parameters: Optional, includes parameters such as temperature, max tokens, top_p, etc.
        :return: The text of the API response.
        """
        if parameters is None:
            parameters = {
                "temperature": 0.7,
                "max_tokens": 10,
                "top_p": 1.0,
            }

        try:
            response = client.chat.completions.create(
                model,
                messages=[{"role": "user", "content": prompt}],
                **parameters
            )
            return response.choices[0].message["content"]
        except Exception as e:
            print(f"Error calling API: {e}")
            return ""

    def add_api_message(self, message: BaseMessage):
        """
        Sends a user message and generates a system response using the DeepSeek API.

        :param message: The BaseMessage object sent by the user.
        """
        self.messages.append(message)

        # Generate the prompt for the API request
        api_prompt = json.dumps(message.content, default=str)

        # Call the API using llm_call
        system_response = llm_call(api_prompt)

        # Generate and add the system response
        if system_response:
            system_message = BaseMessage(
                sender="system",
                receiver=self.conversation_id,
                message_type="system_response",
                content=[{"text": system_response}],
            )
            self.messages.append(system_message)

    def __repr__(self):
        """
        Return a string representation of the conversation.
        """
        return (
            f"Conversation(conversation_id={self.conversation_id}, "
            f"messages={self.messages})"
        )


class BaseAgent:
    """
    A base class for all agents in the system.
    """

    def __init__(self):
        """
        Initialize a new BaseAgent with a unique identifier.
        """
        self.agent_id = str(uuid.uuid4())  # Generate a unique ID for the agent

    def to_json(self) -> str:
        """
        Convert the agent's state to a JSON string.

        :return: A JSON string representing the agent's state.
        """
        return json.dumps({"agent_id": self.agent_id}, indent=4)

    def interact_with_deepseek(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate interaction with the DeepSeek API.

        :param input_data: A dictionary containing input data for the API.
        :return: A dictionary containing the API's response.
        """
        # Simulate a API response
        return {
            "agent_id": self.agent_id,
            "input": input_data,
            "output": {"status": "success", "message": "Processed by DeepSeek API"},
        }

    def __repr__(self):
        """
        Return a string representation of the agent.
        """
        return f"BaseAgent(agent_id={self.agent_id})"


class BaseNetwork:
    def __init__(self, agent_ids, p=0.5):
        """
        Initialize a random directed network using NetworkX.

        Args:
            agent_ids (list): List of agent IDs.
            p (float, optional): Probability of generating a directed edge. Defaults to 0.5.
        """
        self.agent_ids = agent_ids
        self.p = p
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(agent_ids)
        self.generate_random_digraph()
        # Generate a UUID and store it as a string
        self.uuid = str(uuid.uuid4())

    def generate_random_digraph(self):
        """
        Generate a random directed graph with the specified edge probability, ensuring no bidirectional edges.
        """
        for start, end in permutations(self.agent_ids, 2):
            if self.graph.has_edge(end, start):
                continue  # Skip if the reverse edge already exists
            if random.random() <= self.p:
                self.graph.add_edge(start, end)

    def to_json(self):
        """
        Convert the directed graph to a JSON-formatted string.

        Returns:
            str: JSON representation of the directed graph.
        """
        # Convert the graph to a dictionary with node IDs as keys and neighbors as values
        graph_dict = {
            str(node): list(self.graph.successors(node)) for node in self.graph.nodes
        }
        return json.dumps(graph_dict, indent=4)

    def __repr__(self):
        """
        Return the string representation of the object (its UUID).

        Returns:
            str: UUID of the object.
        """
        return self.uuid

    def disconnect_edge(self, start, end):
        """
        Disconnect a specific edge between two nodes.

        Args:
            start: The starting node ID.
            end: The ending node ID.
        """
        if self.graph.has_edge(start, end):
            self.graph.remove_edge(start, end)

    def connect_edge(self, start, end):
        """
        Connect a new edge between two nodes.

        Args:
            start: The starting node ID.
            end: The ending node ID.
        """
        if not self.graph.has_edge(start, end):
            self.graph.add_edge(start, end)

    def reverse_edge(self, start, end):
        """
        Reverse the direction of a specific edge. 

        Args:
            start: The starting node ID.
            end: The ending node ID.

        """
        self.graph.remove_edge(start, end)
        self.graph.add_edge(end, start)

    def agreement(self, start, end):
        """
        Simulate agreement between two nodes to reverse an edge.

        Args:
            start: The starting node ID.
            end: The ending node ID.

        Returns:
            bool: True if both nodes agree, False otherwise.
        """
        # For simplicity, assume both nodes agree 50% of the time
        return random.random() < 0.5

    def execute(self, start, end, method, action):
        """
        Execute an action (reverse, disconnect, or connect) based on the result of the method.

        Args:
            start: The starting node ID.
            end: The ending node ID.
            method: A function that takes (start, end, action) and returns a boolean.
            action: The action to perform ("reverse", "disconnect", or "connect").

        Returns:
            bool: True if the action was executed, False otherwise.
        """
        if method(start, end, action):
            if action == "reverse":
                return self.reverse_edge(start, end)
            elif action == "disconnect":
                self.disconnect_edge(start, end)
                return True
            elif action == "connect":
                self.connect_edge(start, end)
                return True
            else:
                raise ValueError(f"Unknown action: {action}")
        return False


class MessageManager:
    def __init__(self):
        self._messages = []

    def add_message(self, message):
        self._messages.append(message)

    def get_messages(self):
        return list(self._messages)

    def filter_by_metric(self, threshold=0.5):
        return [m for m in self._messages if getattr(m, "contribution_metric", 0) >= threshold]

    def clear_messages(self):
        self._messages.clear()
