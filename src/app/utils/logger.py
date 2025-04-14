import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class APILogger:
    """Logger utility for API operations"""
    
    def __init__(self, name: str = "kma_chat_api"):
        self.logger = logging.getLogger(name)
    
    def _format_log(self, message: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Format the log message with JSON data if provided"""
        if data:
            # Add data as extra props for JSON formatter
            extra = {"props": data}
            return message, extra
        return message, None
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        msg, extra = self._format_log(message, data)
        if extra:
            self.logger.debug(msg, extra=extra)
        else:
            self.logger.debug(msg)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        msg, extra = self._format_log(message, data)
        if extra:
            self.logger.info(msg, extra=extra)
        else:
            self.logger.info(msg)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        msg, extra = self._format_log(message, data)
        if extra:
            self.logger.warning(msg, extra=extra)
        else:
            self.logger.warning(msg)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log error message with optional exception info"""
        msg, extra = self._format_log(message, data)
        if extra:
            self.logger.error(msg, exc_info=exc_info, extra=extra)
        else:
            self.logger.error(msg, exc_info=exc_info)
    
    def critical(self, message: str, data: Optional[Dict[str, Any]] = None, exc_info=None):
        """Log critical message with optional exception info"""
        msg, extra = self._format_log(message, data)
        if extra:
            self.logger.critical(msg, exc_info=exc_info, extra=extra)
        else:
            self.logger.critical(msg, exc_info=exc_info)
    
    def log_request(self, method: str, url: str, status_code: int, 
                   processing_time: float, user_id: Optional[str] = None):
        """Log API request details"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "url": url,
            "status_code": status_code,
            "processing_time_ms": processing_time * 1000,
        }
        
        if user_id:
            log_data["user_id"] = user_id
            
        self.info(f"Request {method} {url} completed with status {status_code}", log_data)
    
    def log_db_operation(self, operation: str, collection: str, 
                         success: bool, data: Optional[Dict[str, Any]] = None):
        """Log database operation details"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "collection": collection,
            "success": success
        }
        
        if data:
            log_data["data"] = data
            
        self.info(f"DB {operation} on {collection}: {'success' if success else 'failed'}", log_data)

# Create a singleton instance for global use
logger = APILogger() 