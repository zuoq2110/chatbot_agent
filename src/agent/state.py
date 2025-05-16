from typing import Dict, List, Any, Optional, Literal, Union
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage


class MyAgentState(BaseModel):
    """State for the Supervisor Agent"""
    
    # Messages
    messages: List[BaseMessage] = Field(default_factory=list)
    
    # Student information
    student_code: Optional[str] = None
    student_name: Optional[str] = None
    student_class: Optional[str] = None
    
    # Score information
    scores: List[Dict[str, Any]] = Field(default_factory=list)
    average_scores: Dict[str, Any] = Field(default_factory=dict)
    
    # RAG information
    rag_results: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Current task info
    current_task: Optional[str] = None
    current_tool: Optional[str] = None
    
    # Human-in-loop control
    awaiting_human_input: bool = False
    human_input_prompt: Optional[str] = None
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the state"""
        self.messages.append(message)
        
    def get_last_message(self) -> Optional[BaseMessage]:
        """Get the last message from the state"""
        if not self.messages:
            return None
        return self.messages[-1]
        
    def get_all_messages(self) -> List[BaseMessage]:
        """Get all messages from the state"""
        return self.messages
        
    def clear_scores(self) -> None:
        """Clear all score data"""
        self.scores = []
        self.average_scores = {}
        
    def set_awaiting_human_input(self, prompt: str) -> None:
        """Set the state to await human input"""
        self.awaiting_human_input = True
        self.human_input_prompt = prompt
        
    def set_human_input_received(self) -> None:
        """Mark human input as received"""
        self.awaiting_human_input = False
        self.human_input_prompt = None
        
    def stored_scores_to_json(self) -> str:
        """Convert stored scores to a JSON string"""
        import json
        return json.dumps({"scores": self.scores})
        
    def update_student_info(self, student_info: Dict[str, Any]) -> None:
        """Update student information"""
        if student_info:
            self.student_code = student_info.get("student_code", self.student_code)
            self.student_name = student_info.get("student_name", self.student_name)
            self.student_class = student_info.get("student_class", self.student_class)
            
    def update_scores(self, scores_data: List[Dict[str, Any]]) -> None:
        """Update score information"""
        if scores_data:
            self.scores = scores_data
            
    def update_average_scores(self, average_data: Dict[str, Any]) -> None:
        """Update average score information"""
        if average_data:
            self.average_scores = average_data
