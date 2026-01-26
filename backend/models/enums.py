from enum import Enum

class RiskLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    CRITICAL = "CRITICAL"

class ModuleType(str, Enum):
    VACCINE = "VACCINE"
    MEDICINE = "MEDICINE"
    BLOOD = "BLOOD"
    AMBULANCE = "AMBULANCE"

class ActionType(str, Enum):
    INSPECTION = "INSPECTION"
    REDISTRIBUTION = "REDISTRIBUTION"
    ESCALATION = "ESCALATION"
    RESCHEDULE = "RESCHEDULE"
    MAINTENANCE = "MAINTENANCE"
