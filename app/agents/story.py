"""Story agent for creating user stories."""
import os
from typing import Any, Dict

from app.agents.base import BaseAgent


class StoryAgent(BaseAgent):
    """Agent for creating user stories."""

    def __init__(self):
        """Initialize story agent."""
        super().__init__(name="StoryAgent")
        self.use_mock = not os.getenv("OPENAI_API_KEY")
        self.llm = None
        
        if not self.use_mock:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model=self.model, temperature=0.7)
            except Exception as e:
                self.log(f"Failed to initialize LLM, using mock mode: {e}", "warning")
                self.use_mock = True

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute story creation.

        Args:
            input_data: Contains 'epics'

        Returns:
            List of user stories
        """
        epics = input_data.get("epics", "")
        self.log("Creating user stories from epics")

        if self.use_mock:
            # Mock user stories response
            stories_data = f"""
# User Stories

## Story 1: User Registration
**Title:** User Account Registration
**User Story:** As a new user, I want to create an account so that I can access the platform features.
**Priority:** Critical
**Acceptance Criteria:**
- User can register with email and password
- Email verification is required
- Password meets security requirements (min 8 chars, special chars)
- User receives confirmation email
- Account is created in the system
**Edge Cases:**
- Duplicate email handling
- Email delivery failures
- Invalid email format
- Network interruptions during registration

## Story 2: User Authentication
**Title:** Secure User Login
**User Story:** As a registered user, I want to securely log in so that I can access my personalized content.
**Priority:** Critical
**Acceptance Criteria:**
- User can log in with email and password
- Failed login attempts are tracked
- Account lockout after 5 failed attempts
- Password reset functionality available
- Session management implemented
**Edge Cases:**
- Expired sessions
- Concurrent login attempts
- Brute force protection
- Social login integration

## Story 3: Dashboard View
**Title:** User Dashboard
**User Story:** As a logged-in user, I want to see a dashboard so that I can quickly access key information and actions.
**Priority:** High
**Acceptance Criteria:**
- Dashboard loads within 2 seconds
- Key metrics displayed prominently
- Quick action buttons available
- Recent activity shown
- Responsive on all devices
**Edge Cases:**
- Empty state for new users
- Large datasets performance
- Offline mode handling
- Real-time updates

## Story 4: Data Import
**Title:** Import External Data
**User Story:** As a user, I want to import data from external sources so that I can consolidate my information.
**Priority:** Medium
**Acceptance Criteria:**
- Support CSV, JSON, XML formats
- Validation of imported data
- Progress indicator during import
- Error reporting for failed imports
- Rollback capability
**Edge Cases:**
- Large file handling (>100MB)
- Malformed data
- Duplicate data detection
- Partial import failures

## Story 5: Data Visualization
**Title:** Interactive Data Charts
**User Story:** As a user, I want to visualize my data in charts so that I can better understand trends and patterns.
**Priority:** Medium
**Acceptance Criteria:**
- Multiple chart types available (bar, line, pie)
- Interactive tooltips
- Export charts as images
- Customizable date ranges
- Real-time data updates
**Edge Cases:**
- No data scenarios
- Performance with large datasets
- Browser compatibility
- Print-friendly formats

## Story 6: Export Functionality
**Title:** Export Reports
**User Story:** As a user, I want to export reports so that I can share data with stakeholders.
**Priority:** Medium
**Acceptance Criteria:**
- Export to PDF, CSV, Excel formats
- Customizable report templates
- Scheduled exports
- Email delivery option
- Download history tracking
**Edge Cases:**
- Large exports timeout handling
- Concurrent export requests
- Template customization limits
- Email delivery failures

## Story 7: User Settings
**Title:** Manage Account Settings
**User Story:** As a user, I want to manage my account settings so that I can personalize my experience.
**Priority:** Low
**Acceptance Criteria:**
- Update profile information
- Change password
- Notification preferences
- Privacy settings
- Theme customization
**Edge Cases:**
- Validation of changes
- Undo functionality
- Settings sync across devices
- Default value restoration

## Story 8: Notifications
**Title:** Real-time Notifications
**User Story:** As a user, I want to receive notifications so that I stay informed about important events.
**Priority:** Medium
**Acceptance Criteria:**
- In-app notifications
- Email notifications (optional)
- Push notifications (optional)
- Notification history
- Mark as read functionality
**Edge Cases:**
- Notification flood prevention
- Offline notification queuing
- Cross-device synchronization
- Do not disturb mode
"""
            return {
                "success": True,
                "stories": stories_data,
                "story_count": 8,
                "priorities": {
                    "critical": 2,
                    "high": 1,
                    "medium": 4,
                    "low": 1
                }
            }

        prompt = f"""
        Based on the following epics, create detailed user stories.
        For each story, provide:
        - Title
        - User story (As a... I want... So that...)
        - Acceptance criteria
        - Priority

        Epics: {epics}

        Format as JSON array.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            stories_data = response.content

            return {
                "success": True,
                "stories": stories_data,
            }
        except Exception as e:
            self.log(f"Story creation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
