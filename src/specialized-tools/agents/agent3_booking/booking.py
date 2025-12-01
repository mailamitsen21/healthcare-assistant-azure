"""
Agent 3: Appointment Booking and Follow-up Agent
Executes SQL queries for booking and checking availability.
"""
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import sys

# Add shared-db to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared-db'))

from cosmos_client import CosmosClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppointmentBooking:
    """
    Handles appointment booking and availability checks.
    """
    
    def __init__(self):
        """Initialize Cosmos DB client."""
        self.cosmos_client = CosmosClient()
        # Support both naming conventions
        self.container_name = os.getenv(
            "COSMOS_DB_APPOINTMENTS_CONTAINER"
        ) or os.getenv(
            "AZURE_COSMOSDB_APPOINTMENTS_CONTAINER",
            "Appointments"
        )
        
        logger.info("AppointmentBooking initialized")
    
    def process_query(self, query: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes appointment-related queries.
        
        Args:
            query: User query text
            input_data: Additional input data (e.g., user_id, date, time)
            
        Returns:
            Dictionary with appointment information or booking result
        """
        try:
            query_lower = query.lower()
            
            # Add query to input_data for use in methods
            input_data["query"] = query
            
            # Determine intent
            if "book" in query_lower or "schedule" in query_lower or "setup" in query_lower or "set up" in query_lower:
                return self._book_appointment(input_data)
            elif "available" in query_lower or "availability" in query_lower:
                return self._check_availability(input_data)
            elif "cancel" in query_lower:
                return self._cancel_appointment(input_data)
            elif "list" in query_lower or "show" in query_lower or "my appointments" in query_lower:
                return self._list_appointments(input_data)
            else:
                # Default to checking availability if intent unclear
                return self._check_availability(input_data)
        except Exception as e:
            logger.error(f"Error processing appointment query: {str(e)}", exc_info=True)
            return {
                "error": f"Error processing appointment request: {str(e)}",
                "message": "I encountered an issue processing your appointment request. Please try again or provide more details."
            }
    
    def _book_appointment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Books a new appointment."""
        try:
            user_id = input_data.get("user_id", "default_user")
            date = input_data.get("date")
            time = input_data.get("time")
            doctor = input_data.get("doctor", "General Practitioner")
            reason = input_data.get("reason", "")
            query = input_data.get("query", "")  # Original query text
            
            # If date/time not provided, suggest available slots
            if not date or not time:
                # Suggest next available date
                from datetime import datetime, timedelta
                next_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                available_slots = self._get_available_slots(next_date, doctor)
                
                return {
                    "error": "Date and time are required for booking",
                    "message": "To book an appointment, please specify a date and time. Here are some available slots:",
                    "suggested_date": next_date,
                    "available_slots": available_slots[:10],  # Top 10 slots
                    "instructions": "Please provide a date (YYYY-MM-DD) and time (HH:MM) to complete your booking."
                }
            
            # Create appointment document
            appointment = {
                "id": f"appt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "user_id": user_id,
                "date": date,
                "time": time,
                "doctor": doctor,
                "reason": reason,
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat()
            }
            
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            # Check if slot is available
            if not self._is_slot_available(date, time, doctor):
                return {
                    "error": "Time slot is not available",
                    "suggested_times": self._get_available_slots(date, doctor)
                }
            
            # Create the appointment
            container.create_item(body=appointment)
            
            logger.info(f"Appointment booked: {appointment['id']}")
            
            return {
                "success": True,
                "appointment_id": appointment["id"],
                "message": f"Appointment scheduled for {date} at {time} with {doctor}"
            }
            
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}", exc_info=True)
            return {"error": f"Failed to book appointment: {str(e)}"}
    
    def _check_availability(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Checks available appointment slots."""
        try:
            date = input_data.get("date", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
            doctor = input_data.get("doctor", "General Practitioner")
            
            available_slots = self._get_available_slots(date, doctor)
            
            return {
                "date": date,
                "doctor": doctor,
                "available_slots": available_slots
            }
            
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}", exc_info=True)
            return {"error": f"Failed to check availability: {str(e)}"}
    
    def _cancel_appointment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancels an appointment."""
        try:
            appointment_id = input_data.get("appointment_id")
            user_id = input_data.get("user_id", "default_user")
            
            if not appointment_id:
                return {"error": "appointment_id is required"}
            
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            # Get the appointment
            appointment = container.read_item(
                item=appointment_id,
                partition_key=user_id
            )
            
            # Update status
            appointment["status"] = "cancelled"
            container.replace_item(
                item=appointment_id,
                body=appointment
            )
            
            return {
                "success": True,
                "message": f"Appointment {appointment_id} has been cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {str(e)}", exc_info=True)
            return {"error": f"Failed to cancel appointment: {str(e)}"}
    
    def _list_appointments(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Lists user's appointments."""
        try:
            user_id = input_data.get("user_id", "default_user")
            
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            query = f"SELECT * FROM c WHERE c.user_id = @user_id AND c.status != 'cancelled' ORDER BY c.date, c.time"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            results = container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            
            appointments = list(results)
            
            return {
                "user_id": user_id,
                "appointments": appointments,
                "count": len(appointments)
            }
            
        except Exception as e:
            logger.error(f"Error listing appointments: {str(e)}", exc_info=True)
            return {"error": f"Failed to list appointments: {str(e)}"}
    
    def _is_slot_available(self, date: str, time: str, doctor: str) -> bool:
        """Checks if a time slot is available."""
        try:
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            query = """
            SELECT COUNT(1) as count
            FROM c
            WHERE c.date = @date
              AND c.time = @time
              AND c.doctor = @doctor
              AND c.status = 'scheduled'
            """
            
            parameters = [
                {"name": "@date", "value": date},
                {"name": "@time", "value": time},
                {"name": "@doctor", "value": doctor}
            ]
            
            results = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            return results[0]["count"] == 0
            
        except Exception as e:
            logger.error(f"Error checking slot availability: {str(e)}")
            return False
    
    def _get_available_slots(self, date: str, doctor: str) -> List[str]:
        """Gets available time slots for a date."""
        # Standard business hours
        time_slots = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00"
        ]
        
        try:
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            query = """
            SELECT c.time
            FROM c
            WHERE c.date = @date
              AND c.doctor = @doctor
              AND c.status = 'scheduled'
            """
            
            parameters = [
                {"name": "@date", "value": date},
                {"name": "@doctor", "value": doctor}
            ]
            
            booked_times = {
                item["time"]
                for item in container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                )
            }
            
            available = [slot for slot in time_slots if slot not in booked_times]
            
            return available
            
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            # Return all slots if query fails
            return time_slots

