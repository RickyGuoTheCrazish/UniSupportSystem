"""
Schedule tools for the Scheduling Assistant Agent in the University Support System.
These functions provide information about academic schedules, deadlines, and policies.

Tools for retrieving academic schedule information.

This module now uses semantic vector embeddings for more natural language understanding.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import os
import numpy as np

from utils.embedding_utils import EmbeddingIndex

# Sample academic calendar - In a real implementation, this would connect to a database
ACADEMIC_CALENDAR = {
    "Fall 2025": {
        "semester_start": "09/01/2025",
        "semester_end": "12/15/2025",
        "registration_start": "07/15/2025",
        "registration_end": "08/20/2025",
        "add_drop_deadline": "09/15/2025",
        "withdrawal_deadline": "10/30/2025",
        "holidays": [
            {"name": "Labor Day", "date": "09/07/2025"},
            {"name": "Fall Break", "date": "10/12/2025 - 10/13/2025"},
            {"name": "Thanksgiving Break", "date": "11/25/2025 - 11/29/2025"}
        ],
        "study_days": "12/16/2025 - 12/17/2025",
        "final_exams": "12/18/2025 - 12/22/2025"
    },
    "Spring 2026": {
        "semester_start": "01/15/2026",
        "semester_end": "05/05/2026",
        "registration_start": "11/15/2025",
        "registration_end": "12/20/2025",
        "add_drop_deadline": "01/29/2026",
        "withdrawal_deadline": "03/15/2026",
        "holidays": [
            {"name": "Martin Luther King Jr. Day", "date": "01/18/2026"},
            {"name": "Spring Break", "date": "03/08/2026 - 03/14/2026"}
        ],
        "study_days": "05/06/2026 - 05/07/2026",
        "final_exams": "05/08/2026 - 05/12/2026"
    },
    "Summer 2026": {
        "semester_start": "06/01/2026",
        "semester_end": "08/15/2026",
        "registration_start": "04/01/2026",
        "registration_end": "05/15/2026",
        "add_drop_deadline": "06/10/2026",
        "withdrawal_deadline": "07/15/2026",
        "holidays": [
            {"name": "Independence Day", "date": "07/04/2026"}
        ],
        "study_days": "08/16/2026",
        "final_exams": "08/17/2026 - 08/18/2026"
    }
}

# Sample university policies
UNIVERSITY_POLICIES = {
    "add_drop": "Students may add or drop courses without penalty during the first two weeks of the semester. "
                "After the add/drop deadline, students cannot add courses but may withdraw with a 'W' grade.",
    
    "withdrawal": "Course withdrawal is allowed until the withdrawal deadline. A grade of 'W' will appear on the transcript. "
                 "After the withdrawal deadline, students will receive the grade earned in the course.",
    
    "graduation": "Students must submit a graduation application at least one semester before their intended "
                 "graduation date. All degree requirements must be completed by the end of the final semester.",
    
    "enrollment": "Full-time enrollment requires at least 12 credit hours per semester for undergraduates and "
                 "9 credit hours for graduate students. International students must maintain full-time enrollment.",
    
    "attendance": "Regular attendance is expected in all courses. Students who miss more than 25% of class sessions "
                 "may be administratively withdrawn at the instructor's discretion.",
    
    "incomplete": "An 'Incomplete' grade may be assigned when a student cannot complete coursework due to "
                 "circumstances beyond their control. Remaining work must be completed within one semester."
}

# Sample class schedules
CLASS_SCHEDULE_PATTERNS = {
    "MWF": "Monday, Wednesday, Friday",
    "TR": "Tuesday, Thursday",
    "MW": "Monday, Wednesday",
    "M": "Monday only",
    "T": "Tuesday only",
    "W": "Wednesday only",
    "R": "Thursday only",
    "F": "Friday only",
    "S": "Saturday only"
}

# Sample class times
CLASS_TIMES = [
    "8:00 AM - 9:15 AM",
    "9:30 AM - 10:45 AM",
    "11:00 AM - 12:15 PM",
    "12:30 PM - 1:45 PM",
    "2:00 PM - 3:15 PM",
    "3:30 PM - 4:45 PM",
    "5:00 PM - 6:15 PM",
    "6:30 PM - 7:45 PM",
    "8:00 PM - 9:15 PM"
]


def get_semester_dates(context_variables: Dict[str, Any], semester: str) -> str:
    """
    Get important dates for a specific semester.
    
    Args:
        context_variables: Context variables for the conversation
        semester: The semester to get dates for (e.g., "Fall 2025")
        
    Returns:
        String with important dates for the specified semester
    """
    # Convert to title case to match our dictionary keys
    semester = semester.title()
    
    # Check if we have data for this semester
    if semester not in ACADEMIC_CALENDAR:
        available_semesters = ", ".join(ACADEMIC_CALENDAR.keys())
        return f"Information for {semester} is not available. I have data for: {available_semesters}."
    
    # Get the semester data
    sem_data = ACADEMIC_CALENDAR[semester]
    
    # Format the response
    result = f"Important dates for {semester}:\n\n"
    result += f"Semester start: {sem_data['semester_start']}\n"
    result += f"Semester end: {sem_data['semester_end']}\n\n"
    
    result += f"Registration period: {sem_data['registration_start']} to {sem_data['registration_end']}\n"
    result += f"Add/drop deadline: {sem_data['add_drop_deadline']}\n"
    result += f"Withdrawal deadline: {sem_data['withdrawal_deadline']}\n\n"
    
    result += "Holidays and breaks:\n"
    for holiday in sem_data['holidays']:
        result += f"- {holiday['name']}: {holiday['date']}\n"
    
    result += f"\nStudy days: {sem_data['study_days']}\n"
    result += f"Final exams: {sem_data['final_exams']}\n"
    
    return result


def describe_drop_policy(context_variables: Dict[str, Any]) -> str:
    """
    Describe the university's course drop and withdrawal policy.
    
    Args:
        context_variables: Context variables for the conversation
        
    Returns:
        String with the drop/withdrawal policy information
    """
    # Get the current semester based on date (this is a simple approximation)
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    if 1 <= current_month <= 5:
        current_semester = f"Spring {current_year}"
    elif 6 <= current_month <= 8:
        current_semester = f"Summer {current_year}"
    else:
        current_semester = f"Fall {current_year}"
    
    # Find the closest semester in our calendar
    closest_semester = None
    for semester in ACADEMIC_CALENDAR.keys():
        if current_semester in semester or semester in current_semester:
            closest_semester = semester
            break
    
    if not closest_semester:
        closest_semester = list(ACADEMIC_CALENDAR.keys())[0]
    
    # Get the relevant dates
    add_drop_deadline = ACADEMIC_CALENDAR[closest_semester]["add_drop_deadline"]
    withdrawal_deadline = ACADEMIC_CALENDAR[closest_semester]["withdrawal_deadline"]
    
    # Construct the result
    result = "University Course Drop/Withdrawal Policy:\n\n"
    result += UNIVERSITY_POLICIES["add_drop"] + "\n\n"
    result += UNIVERSITY_POLICIES["withdrawal"] + "\n\n"
    
    result += f"For {closest_semester}:\n"
    result += f"Add/drop deadline: {add_drop_deadline}\n"
    result += f"Withdrawal deadline: {withdrawal_deadline}\n\n"
    
    result += "Important notes:\n"
    result += "- Dropping a course before the add/drop deadline removes it completely from your record.\n"
    result += "- Withdrawing after the add/drop deadline but before the withdrawal deadline results in a 'W' grade.\n"
    result += "- After the withdrawal deadline, you will receive the grade earned in the course.\n"
    result += "- Always consult with your academic advisor before dropping or withdrawing from courses."
    
    return result


def check_enrollment_status(context_variables: Dict[str, Any], credit_hours: int) -> str:
    """
    Check enrollment status based on credit hours.
    
    Args:
        context_variables: Context variables for the conversation
        credit_hours: Number of credit hours the student is enrolled in
        
    Returns:
        String with enrollment status information
    """
    # Determine enrollment status
    if credit_hours < 6:
        status = "Less than half-time"
        financial_aid = "Limited eligibility for financial aid. Most loans and scholarships require at least half-time enrollment."
    elif credit_hours < 9:
        status = "Half-time"
        financial_aid = "Eligible for some financial aid options, including some federal loans. Not eligible for full financial aid packages."
    elif credit_hours < 12:
        status = "Three-quarter time"
        financial_aid = "Eligible for many financial aid options, but not considered full-time for some scholarships and grants."
    else:
        status = "Full-time"
        financial_aid = "Eligible for full financial aid consideration, including maximum loan amounts, scholarships, and grants."
    
    # Construct the result
    result = f"Enrollment status for {credit_hours} credit hours: {status}\n\n"
    
    result += "Status implications:\n"
    result += f"- Financial aid: {financial_aid}\n"
    
    if status == "Full-time":
        result += "- Housing: Eligible for on-campus housing priority.\n"
        result += "- Athletics: Meets NCAA eligibility requirements.\n"
        result += "- International students: Meets F-1/J-1 visa requirements.\n"
    else:
        result += "- Housing: May affect eligibility for certain on-campus housing options.\n"
        
        if status == "Less than half-time":
            result += "- Athletics: Does not meet NCAA eligibility requirements.\n"
            result += "- International students: Does not meet F-1/J-1 visa requirements.\n"
        else:
            result += "- Athletics: May not meet NCAA eligibility requirements. Consult with athletic department.\n"
            result += "- International students: Does not meet F-1/J-1 visa requirements.\n"


def get_exam_schedule(context_variables: Dict[str, Any], semester: str = None) -> str:
    """
    Get the final exam schedule for a specified semester.
    
    Args:
        context_variables: Context variables for the conversation
        semester: The semester to get the exam schedule for (defaults to current/next semester)
        
    Returns:
        String with the final exam schedule information
    """
    # If no semester specified, determine current/next semester
    if not semester:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        if 1 <= current_month <= 5:
            semester = f"Spring {current_year}"
        elif 6 <= current_month <= 8:
            semester = f"Summer {current_year}"
        else:
            semester = f"Fall {current_year}"
    
    # Normalize the semester format
    semester = semester.title()
    
    # Check if we have data for this semester
    if semester not in ACADEMIC_CALENDAR:
        available_semesters = ", ".join(ACADEMIC_CALENDAR.keys())
        return f"Exam schedule for {semester} is not available. I have data for: {available_semesters}."
    
    # Get the exam period
    study_days = ACADEMIC_CALENDAR[semester]["study_days"]
    exam_period = ACADEMIC_CALENDAR[semester]["final_exams"]
    
    # Construct a simple exam schedule based on class meeting patterns
    result = f"Final Exam Schedule for {semester}:\n\n"
    result += f"Study days: {study_days}\n"
    result += f"Exam period: {exam_period}\n\n"
    
    result += "Exam schedule by class meeting pattern:\n\n"
    
    # Create a basic mapping of class patterns to exam dates (simplified)
    exam_start_date = exam_period.split(" - ")[0]
    
    result += f"MWF classes:\n"
    result += f"- 8:00 AM - 9:15 AM: {exam_start_date} at 8:00 AM\n"
    result += f"- 9:30 AM - 10:45 AM: {exam_start_date} at 10:30 AM\n"
    result += f"- 11:00 AM - 12:15 PM: {exam_start_date} at 1:00 PM\n"
    result += f"- Afternoon classes: {exam_start_date} at 3:30 PM\n\n"
    
    # Calculate next day (very simplified)
    day_parts = exam_start_date.split("/")
    next_day = f"{day_parts[0]}/{int(day_parts[1]) + 1}/{day_parts[2]}"
    
    result += f"TR classes:\n"
    result += f"- 8:00 AM - 9:15 AM: {next_day} at 8:00 AM\n"
    result += f"- 9:30 AM - 10:45 AM: {next_day} at 10:30 AM\n"
    result += f"- 11:00 AM - 12:15 PM: {next_day} at 1:00 PM\n"
    result += f"- Afternoon classes: {next_day} at 3:30 PM\n\n"
    
    result += "Note: Evening classes, online classes, and classes with irregular meeting patterns will have "
    result += "exams scheduled by the instructor. Please confirm all exam times with your instructors."
    
    return result
