"""Epic agent for creating epics."""
import os
from typing import Any, Dict, List

from app.agents.base import BaseAgent


class EpicAgent(BaseAgent):
    """Agent for creating product epics."""

    def __init__(self):
        """Initialize epic agent."""
        super().__init__(name="EpicAgent")
        self.use_mock = not os.getenv("OPENAI_API_KEY")
        
        if not self.use_mock:
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model=self.model, temperature=0.7)
            except Exception as e:
                self.log(f"Failed to initialize LLM, using mock mode: {e}", "warning")
                self.use_mock = True

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute epic creation.

        Args:
            input_data: Contains 'product_idea' and 'research'

        Returns:
            List of epics
        """
        product_idea = input_data.get("product_idea", "")
        research = input_data.get("research", "")

        self.log(f"Creating epics for: {product_idea}")

        if self.use_mock:
            # Mock epic response
            epics_data = f"""
# Epics for: {product_idea}

## Epic 1: Core Platform Foundation
**Title:** Build Core Platform Infrastructure
**Goal:** Establish the foundational architecture and core services
**Scope:** Backend services, database, authentication, basic API
**Priority:** 1 (Critical)
**Dependencies:** None
**Risks:** Technical complexity, scalability concerns
**Acceptance Criteria:**
- Scalable microservices architecture deployed
- User authentication and authorization working
- Core API endpoints operational
- Database schema implemented

## Epic 2: User Interface Development
**Title:** Design and Implement User Interface
**Goal:** Create intuitive and responsive user interface
**Scope:** Frontend application, UI components, user workflows
**Priority:** 2 (High)
**Dependencies:** Epic 1
**Risks:** UX complexity, browser compatibility
**Acceptance Criteria:**
- Responsive design across devices
- Key user workflows implemented
- Accessibility standards met
- Performance benchmarks achieved

## Epic 3: Integration and Data Management
**Title:** Third-Party Integrations and Data Pipeline
**Goal:** Enable data exchange with external systems
**Scope:** API integrations, data import/export, webhooks
**Priority:** 3 (Medium)
**Dependencies:** Epic 1
**Risks:** Third-party API changes, data consistency
**Acceptance Criteria:**
- Key integrations functional
- Data sync mechanisms working
- Error handling implemented
- Documentation complete

## Epic 4: Analytics and Reporting
**Title:** Analytics Dashboard and Reporting System
**Goal:** Provide insights through data visualization
**Scope:** Analytics engine, dashboards, custom reports
**Priority:** 4 (Medium)
**Dependencies:** Epic 1, Epic 3
**Risks:** Data processing performance
**Acceptance Criteria:**
- Real-time analytics available
- Custom report generation working
- Data export capabilities
- Performance within SLA

## Epic 5: Security and Compliance
**Title:** Security Hardening and Compliance
**Goal:** Ensure security best practices and regulatory compliance
**Scope:** Security audit, compliance features, monitoring
**Priority:** 2 (High)
**Dependencies:** Epic 1
**Risks:** Regulatory changes, security vulnerabilities
**Acceptance Criteria:**
- Security audit passed
- Compliance requirements met
- Monitoring and alerting active
- Incident response plan documented
"""
            return {
                "success": True,
                "epics": epics_data,
                "product_idea": product_idea,
                "epic_count": 5,
                "priorities": {
                    "critical": 1,
                    "high": 2,
                    "medium": 2
                }
            }

        prompt = f"""
        Based on the following product idea and research, create 3-5 high-level epics.
        For each epic, provide:
        - Title
        - Description
        - Acceptance Criteria
        - Priority (1-5)

        Product Idea: {product_idea}
        Research: {research}

        Format as JSON array.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            # Simplified - in production, parse JSON properly
            epics_data = response.content

            return {
                "success": True,
                "epics": epics_data,
                "product_idea": product_idea,
            }
        except Exception as e:
            self.log(f"Epic creation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
