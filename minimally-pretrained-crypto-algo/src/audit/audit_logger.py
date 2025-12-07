"""
Comprehensive Audit Logging System
Full financial audit trail with tamper detection.
"""

import json
import hashlib
import asyncio
from decimal import Decimal
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import aiofiles
from loguru import logger


class AuditEventType(Enum):
    """Types of auditable events."""
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIG_LOAD = "config_load"
    
    # Trading events
    ROUND_START = "round_start"
    ROUND_END = "round_end"
    PATH_DISCOVERED = "path_discovered"
    ALLOCATION_DECISION = "allocation_decision"
    
    # Execution events
    ORDER_SUBMITTED = "order_submitted"
    ORDER_FILLED = "order_filled"
    ORDER_FAILED = "order_failed"
    ORDER_CANCELLED = "order_cancelled"
    
    # Financial events
    PROFIT_RECORDED = "profit_recorded"
    LOSS_RECORDED = "loss_recorded"
    FEE_PAID = "fee_paid"
    BALANCE_UPDATE = "balance_update"
    
    # Risk events
    RISK_ALERT = "risk_alert"
    CIRCUIT_BREAKER = "circuit_breaker"
    DAILY_LIMIT_HIT = "daily_limit_hit"
    
    # Learning events
    PATH_SUCCESS_RECORDED = "path_success_recorded"
    PATH_FAILURE_RECORDED = "path_failure_recorded"
    PROBABILITY_UPDATED = "probability_updated"


@dataclass
class AuditEvent:
    """Single audit log entry."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    data: Dict[str, Any]
    previous_hash: str
    current_hash: str = field(default='')
    
    def __post_init__(self):
        if not self.current_hash:
            self.current_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate tamper-proof hash of event."""
        content = f"{self.event_id}:{self.event_type.value}:{self.timestamp.isoformat()}:{json.dumps(self.data, sort_keys=True, default=str)}:{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify event hasn't been tampered with."""
        return self._calculate_hash() == self.current_hash
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'current_hash': self.current_hash
        }


class AuditLogger:
    """
    Comprehensive audit logging with blockchain-style integrity.
    
    Features:
    - Tamper-proof hash chain
    - Async file writing
    - Structured JSON logs
    - Event categorization
    - Integrity verification
    """
    
    def __init__(self, log_dir: str, retention_days: int = 365):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        
        self._events: List[AuditEvent] = []
        self._event_counter = 0
        self._last_hash = "GENESIS"
        self._lock = asyncio.Lock()
        
        # Current log file
        self._current_file: Optional[Path] = None
        self._init_log_file()
    
    def _init_log_file(self) -> None:
        """Initialize or rotate log file."""
        date_str = datetime.now().strftime('%Y%m%d')
        self._current_file = self.log_dir / f"audit_{date_str}.jsonl"
        
        # Load last hash if file exists
        if self._current_file.exists():
            try:
                with open(self._current_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        self._last_hash = last_event.get('current_hash', 'GENESIS')
                        self._event_counter = len(lines)
            except Exception as e:
                logger.warning(f"Could not read existing audit log: {e}")
    
    async def log(
        self,
        event_type: AuditEventType,
        data: Dict[str, Any],
        immediate_write: bool = True
    ) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            data: Event data
            immediate_write: Write to file immediately
            
        Returns:
            Created AuditEvent
        """
        async with self._lock:
            self._event_counter += 1
            event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._event_counter:06d}"
            
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.now(),
                data=data,
                previous_hash=self._last_hash
            )
            
            self._events.append(event)
            self._last_hash = event.current_hash
            
            if immediate_write:
                await self._write_event(event)
            
            return event
    
    async def _write_event(self, event: AuditEvent) -> None:
        """Write event to log file."""
        try:
            async with aiofiles.open(self._current_file, 'a') as f:
                await f.write(json.dumps(event.to_dict(), default=str) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit event: {e}")
    
    async def log_system_start(self, config: Dict[str, Any]) -> AuditEvent:
        """Log system startup."""
        # Sanitize sensitive data
        safe_config = {k: v for k, v in config.items() if 'secret' not in k.lower() and 'key' not in k.lower()}
        return await self.log(AuditEventType.SYSTEM_START, {'config': safe_config})
    
    async def log_round_start(
        self,
        round_id: str,
        capital: str,
        num_groups: int
    ) -> AuditEvent:
        """Log trading round start."""
        return await self.log(
            AuditEventType.ROUND_START,
            {
                'round_id': round_id,
                'capital': capital,
                'num_groups': num_groups
            }
        )
    
    async def log_round_end(
        self,
        round_id: str,
        profit: str,
        fees: str,
        success_count: int,
        failure_count: int
    ) -> AuditEvent:
        """Log trading round completion."""
        return await self.log(
            AuditEventType.ROUND_END,
            {
                'round_id': round_id,
                'profit': profit,
                'fees': fees,
                'successes': success_count,
                'failures': failure_count
            }
        )
    
    async def log_order(
        self,
        event_type: AuditEventType,
        order_data: Dict[str, Any]
    ) -> AuditEvent:
        """Log order event."""
        return await self.log(event_type, order_data)
    
    async def log_path_result(
        self,
        path_str: str,
        success: bool,
        expected_profit: str,
        actual_profit: str,
        currencies: List[str]
    ) -> AuditEvent:
        """Log path execution result."""
        event_type = AuditEventType.PATH_SUCCESS_RECORDED if success else AuditEventType.PATH_FAILURE_RECORDED
        return await self.log(
            event_type,
            {
                'path': path_str,
                'success': success,
                'expected_profit': expected_profit,
                'actual_profit': actual_profit,
                'currencies': currencies
            }
        )
    
    async def log_risk_event(
        self,
        event_type: AuditEventType,
        reason: str,
        current_loss: str,
        threshold: str
    ) -> AuditEvent:
        """Log risk management event."""
        return await self.log(
            event_type,
            {
                'reason': reason,
                'current_loss': current_loss,
                'threshold': threshold
            }
        )
    
    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """
        Verify integrity of the entire audit chain.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self._events:
            return True, []
        
        # Check first event
        if self._events[0].previous_hash != "GENESIS":
            errors.append(f"First event has invalid genesis hash")
        
        # Check chain
        for i in range(len(self._events)):
            event = self._events[i]
            
            # Verify hash
            if not event.verify_integrity():
                errors.append(f"Event {event.event_id} has invalid hash")
            
            # Verify chain linkage
            if i > 0:
                if event.previous_hash != self._events[i-1].current_hash:
                    errors.append(f"Event {event.event_id} has broken chain link")
        
        return len(errors) == 0, errors
    
    def get_events_by_type(self, event_type: AuditEventType) -> List[AuditEvent]:
        """Get all events of a specific type."""
        return [e for e in self._events if e.event_type == event_type]
    
    def get_events_in_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[AuditEvent]:
        """Get events within a time range."""
        return [
            e for e in self._events 
            if start <= e.timestamp <= end
        ]
    
    async def generate_audit_report(self, output_path: str) -> None:
        """Generate comprehensive audit report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_events': len(self._events),
            'chain_valid': self.verify_chain_integrity()[0],
            'events_by_type': {},
            'timeline': []
        }
        
        # Count by type
        for event_type in AuditEventType:
            count = len([e for e in self._events if e.event_type == event_type])
            if count > 0:
                report['events_by_type'][event_type.value] = count
        
        # Add recent events to timeline
        report['timeline'] = [e.to_dict() for e in self._events[-100:]]
        
        async with aiofiles.open(output_path, 'w') as f:
            await f.write(json.dumps(report, indent=2, default=str))
        
        logger.info(f"Audit report generated: {output_path}")
