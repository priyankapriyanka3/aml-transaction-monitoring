"""Alert repository for data access."""
import uuid
from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.customer import Customer


class AlertRepository:
    """Repository for alert data access with prioritization and filtering."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_prioritized(
        self,
        priority: str | None = None,
        ownership: str | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
        current_user_id: uuid.UUID | None = None,
    ) -> tuple[list, int]:
        """
        List alerts with prioritization, filtering, search, and pagination.
        
        Default ordering: risk_score DESC, triggered_at_utc DESC
        
        Args:
            priority: Filter by priority (Critical, High, Medium, Low)
            ownership: Filter by ownership (All, Unassigned, Assigned to Me)
            status: Filter by status (New, Under Review, Escalated, Resolved)
            search: Search by alert_ref or customer_name
            page: Page number (1-indexed)
            page_size: Items per page
            current_user_id: Current user ID for "Assigned to Me" filter
        
        Returns:
            Tuple of (alert list with joined data, total count)
        """
        # Base query with joins
        query = (
            select(
                Alert,
                Transaction.amount,
                Transaction.currency_code,
                Transaction.source_country_code,
                Transaction.destination_country_code,
                Customer.customer_id,
                Customer.customer_name
            )
            .join(Transaction, Alert.transaction_id == Transaction.transaction_id)
            .join(Customer, Alert.customer_id == Customer.customer_id)
        )
        
        # Apply filters
        if priority:
            query = query.where(Alert.priority == priority)
        
        if ownership:
            if ownership == "Unassigned":
                query = query.where(Alert.owner_user_id.is_(None))
            elif ownership == "Assigned to Me" and current_user_id:
                query = query.where(Alert.owner_user_id == current_user_id)
        
        if status:
            query = query.where(Alert.status == status)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Alert.alert_ref.ilike(search_pattern)) |
                (Customer.customer_name.ilike(search_pattern))
            )
        
        # Count total before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar_one()
        
        # Apply ordering: risk_score DESC, triggered_at_utc DESC
        query = query.order_by(desc(Alert.risk_score), desc(Alert.triggered_at_utc))
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Execute and return
        results = self.db.execute(query).all()
        
        # Transform results into dictionaries with joined data
        alert_items = []
        for row in results:
            alert, amount, currency_code, source_country, dest_country, customer_id, customer_name = row
            alert_items.append({
                "alert_id": alert.alert_id,
                "alert_ref": alert.alert_ref,
                "priority": alert.priority,
                "risk_score": alert.risk_score,
                "status": alert.status,
                "owner_user_id": alert.owner_user_id,
                "triggered_at_utc": alert.triggered_at_utc,
                "transaction_amount": amount,
                "transaction_currency_code": currency_code,
                "source_country_code": source_country,
                "destination_country_code": dest_country,
                "customer_id": customer_id,
                "customer_name": customer_name,
            })
        
        return alert_items, total
    
    def get_by_id(self, alert_id: uuid.UUID) -> Alert | None:
        """Get alert by ID."""
        return self.db.get(Alert, alert_id)
    
    def update(self, alert: Alert) -> Alert:
        """Update alert and commit."""
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
