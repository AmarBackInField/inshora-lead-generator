"""Base utility tools for the telephony agent."""

import logging
from datetime import datetime
from livekit.agents import function_tool, RunContext

logger = logging.getLogger("telephony-agent")


class BaseTools:
    """Base utility tools for common operations."""
    
    @staticmethod
    @function_tool()
    async def get_current_time(context: RunContext) -> str:
        """Get the current time.
        
        Returns:
            Current time in 12-hour format.
        """
        return f"The current time is {datetime.now().strftime('%I:%M %p')}"

