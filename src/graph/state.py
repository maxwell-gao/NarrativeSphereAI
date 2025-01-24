import json
from ..agent.state import AgentState
from flow import InformationFlow
from typing import Any, Dict, List
from uuid import uuid4
from ..common.base import BaseNetwork


class WorldState:
    """
    Represents the state of the world, including the base network, global/local events,
    agent states, and global narrative motifs.
    """

    def __init__(
        self,
        agent_list: List[str] = None,
        base_network: BaseNetwork = None,
        global_events: List[Dict[str, Any]] = None,
        local_events: List[Dict[str, Any]] = None,
        agent_states: List[Dict[str, Any]] = None,
        global_motifs: List[str] = None
    ):
        """
        Initialize a new WorldState.

        :param base_network: A dictionary representing the base network structure.
        :param global_events: A list of global/public events.
        :param local_events: A list of local/private events.
        :param agent_states: A list of agent states.
        :param global_motifs: A list of global narrative motifs.
        """
        self.base_network = base_network(
            agent_list) if base_network is not None else {}
        self.global_events = global_events if global_events is not None else []
        self.local_events = local_events if local_events is not None else []
        self.agent_states = agent_states if agent_states is not None else []
        self.global_motifs = global_motifs if global_motifs is not None else []

    def to_json(self):
        """
        Serialize the world state to a JSON string.

        :return: A JSON string representing the world state.
        """
        return json.dumps({
            "base_network": self.base_network,
            "global_events": self.global_events,
            "local_events": self.local_events,
            "agent_states": self.agent_states,
            "global_motifs": self.global_motifs
        }, indent=4)

    @classmethod
    def from_json(cls, json_str: str):
        """
        Deserialize a JSON string into a WorldState object.

        :param json_str: A JSON string representing the world state.
        :return: A WorldState object.
        """
        data = json.loads(json_str)
        return cls(
            base_network=data.get("base_network", {}),
            global_events=data.get("global_events", []),
            local_events=data.get("local_events", []),
            agent_states=data.get("agent_states", []),
            global_motifs=data.get("global_motifs", [])
        )

    def __repr__(self):
        """
        Return a string representation of the world state.
        """
        return (f"WorldState(base_network={self.base_network}, global_events={self.global_events}, "
                f"local_events={self.local_events}, agent_states={self.agent_states}, "
                f"global_motifs={self.global_motifs})")
