"""
Comprehensive Financial Tracking
Full P&L tracking, fee analysis, and financial reporting.
"""

from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, date
from collections import defaultdict
import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from loguru import logger


@dataclass
class TradeRecord:
    """Complete record of a single trade."""
    trade_id: str
    round_id: str
    group_id: int
    timestamp: datetime
    
    # Path info
    path_str: str
    currencies: List[str]
    chain_length: int
    
    # Allocation
    allocation: Decimal
    probability: float
    confidence: str
    
    # Execution
    executed: bool
    start_amount: Decimal
    end_amount: Decimal
    
    # Financial
    gross_profit: Decimal
    total_fees: Decimal
    net_profit: Decimal
    profit_percent: Decimal
    
    # Analysis
    expected_profit: Decimal
    slippage: Decimal
    execution_time_ms: float
    
    # Status
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trade_id': self.trade_id,
            'round_id': self.round_id,
            'group_id': self.group_id,
            'timestamp': self.timestamp.isoformat(),
            'path': self.path_str,
            'currencies': self.currencies,
            'chain_length': self.chain_length,
            'allocation': str(self.allocation),
            'probability': self.probability,
            'confidence': self.confidence,
            'executed': self.executed,
            'start_amount': str(self.start_amount),
            'end_amount': str(self.end_amount),
            'gross_profit': str(self.gross_profit),
            'total_fees': str(self.total_fees),
            'net_profit': str(self.net_profit),
            'profit_percent': str(self.profit_percent),
            'expected_profit': str(self.expected_profit),
            'slippage': str(self.slippage),
            'execution_time_ms': self.execution_time_ms,
            'success': self.success,
            'error': self.error_message
        }


@dataclass
class DailySummary:
    """Daily financial summary."""
    date: date
    start_balance: Decimal
    end_balance: Decimal
    gross_profit: Decimal
    total_fees: Decimal
    net_profit: Decimal
    trade_count: int
    successful_trades: int
    failed_trades: int
    win_rate: float
    best_trade: Decimal
    worst_trade: Decimal
    avg_trade_profit: Decimal
    total_allocation: Decimal


class FinancialTracker:
    """
    Comprehensive financial tracking and reporting.
    
    Features:
    - Real-time P&L tracking
    - Fee analysis by product/currency
    - Daily/weekly/monthly summaries
    - Excel reporting with charts
    - What went right/wrong analysis
    """
    
    def __init__(self, excel_path: str, metrics_path: str):
        self.excel_path = Path(excel_path)
        self.metrics_path = Path(metrics_path)
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        self.trades: List[TradeRecord] = []
        self.daily_summaries: Dict[date, DailySummary] = {}
        
        # Real-time tracking
        self.current_balance = Decimal('0')
        self.starting_balance = Decimal('0')
        self.total_profit = Decimal('0')
        self.total_fees = Decimal('0')
        
        # Analysis tracking
        self.profit_by_currency: Dict[str, Decimal] = defaultdict(Decimal)
        self.fees_by_product: Dict[str, Decimal] = defaultdict(Decimal)
        self.success_by_path: Dict[str, Dict] = defaultdict(lambda: {'wins': 0, 'losses': 0, 'profit': Decimal('0')})
        
        self._ensure_excel_exists()
    
    def _ensure_excel_exists(self) -> None:
        """Create Excel workbook if it doesn't exist."""
        if not self.excel_path.exists():
            self._create_workbook()
    
    def _create_workbook(self) -> None:
        """Create new Excel workbook with all sheets."""
        wb = Workbook()
        
        sheets = {
            'Trade Log': [
                'Trade ID', 'Timestamp', 'Round', 'Group', 'Path', 'Chain Length',
                'Allocation', 'Probability', 'Confidence', 'Start', 'End',
                'Gross Profit', 'Fees', 'Net Profit', 'Profit %', 'Success', 'Error'
            ],
            'Daily Summary': [
                'Date', 'Start Balance', 'End Balance', 'Gross Profit', 'Fees',
                'Net Profit', 'Trades', 'Wins', 'Losses', 'Win Rate %',
                'Best Trade', 'Worst Trade', 'Avg Profit'
            ],
            'Currency Analysis': [
                'Currency', 'Times Traded', 'Total Profit', 'Avg Profit',
                'Success Rate %', 'Total Fees'
            ],
            'Path Performance': [
                'Path', 'Times Used', 'Wins', 'Losses', 'Win Rate %',
                'Total Profit', 'Avg Profit', 'Best Result', 'Worst Result'
            ],
            'What Worked': [
                'Category', 'Description', 'Impact', 'Frequency', 'Recommendation'
            ],
            'What Failed': [
                'Category', 'Description', 'Loss Amount', 'Frequency', 'Fix'
            ],
            'Fee Analysis': [
                'Product', 'Trade Count', 'Total Fees', 'Avg Fee', 'Fee %'
            ],
            'Performance Metrics': [
                'Metric', 'Value', 'Notes'
            ]
        }
        
        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            del wb['Sheet']
        
        for sheet_name, headers in sheets.items():
            ws = wb.create_sheet(sheet_name)
            self._write_headers(ws, headers)
        
        wb.save(self.excel_path)
        logger.info(f"Created Excel workbook: {self.excel_path}")
    
    def _write_headers(self, ws, headers: List[str]) -> None:
        """Write styled headers to worksheet."""
        header_font = Font(bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            ws.column_dimensions[cell.column_letter].width = max(len(header) + 2, 12)
    
    def record_trade(self, trade: TradeRecord) -> None:
        """Record a completed trade."""
        self.trades.append(trade)
        
        # Update running totals
        self.total_profit += trade.net_profit
        self.total_fees += trade.total_fees
        
        # Update currency tracking
        for currency in trade.currencies:
            self.profit_by_currency[currency] += trade.net_profit / len(trade.currencies)
        
        # Update path tracking
        path_stats = self.success_by_path[trade.path_str]
        path_stats['profit'] += trade.net_profit
        if trade.success:
            path_stats['wins'] += 1
        else:
            path_stats['losses'] += 1
        
        # Write to Excel
        self._append_trade_to_excel(trade)
    
    def _append_trade_to_excel(self, trade: TradeRecord) -> None:
        """Append trade record to Excel."""
        try:
            wb = load_workbook(self.excel_path)
            ws = wb['Trade Log']
            
            row = [
                trade.trade_id,
                trade.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                trade.round_id,
                trade.group_id,
                trade.path_str,
                trade.chain_length,
                float(trade.allocation),
                trade.probability,
                trade.confidence,
                float(trade.start_amount),
                float(trade.end_amount),
                float(trade.gross_profit),
                float(trade.total_fees),
                float(trade.net_profit),
                float(trade.profit_percent),
                'Yes' if trade.success else 'No',
                trade.error_message or ''
            ]
            ws.append(row)
            wb.save(self.excel_path)
            
        except Exception as e:
            logger.error(f"Failed to write trade to Excel: {e}")
    
    def update_daily_summary(self, today: date = None) -> DailySummary:
        """Calculate and store daily summary."""
        today = today or date.today()
        
        # Get today's trades
        day_trades = [t for t in self.trades if t.timestamp.date() == today]
        
        if not day_trades:
            return None
        
        wins = sum(1 for t in day_trades if t.success)
        losses = len(day_trades) - wins
        
        profits = [t.net_profit for t in day_trades]
        
        summary = DailySummary(
            date=today,
            start_balance=self.starting_balance,
            end_balance=self.current_balance,
            gross_profit=sum(t.gross_profit for t in day_trades),
            total_fees=sum(t.total_fees for t in day_trades),
            net_profit=sum(profits),
            trade_count=len(day_trades),
            successful_trades=wins,
            failed_trades=losses,
            win_rate=(wins / len(day_trades) * 100) if day_trades else 0,
            best_trade=max(profits) if profits else Decimal('0'),
            worst_trade=min(profits) if profits else Decimal('0'),
            avg_trade_profit=sum(profits) / len(profits) if profits else Decimal('0'),
            total_allocation=sum(t.allocation for t in day_trades)
        )
        
        self.daily_summaries[today] = summary
        self._write_daily_summary(summary)
        
        return summary
    
    def _write_daily_summary(self, summary: DailySummary) -> None:
        """Write daily summary to Excel."""
        try:
            wb = load_workbook(self.excel_path)
            ws = wb['Daily Summary']
            
            row = [
                summary.date.strftime('%Y-%m-%d'),
                float(summary.start_balance),
                float(summary.end_balance),
                float(summary.gross_profit),
                float(summary.total_fees),
                float(summary.net_profit),
                summary.trade_count,
                summary.successful_trades,
                summary.failed_trades,
                summary.win_rate,
                float(summary.best_trade),
                float(summary.worst_trade),
                float(summary.avg_trade_profit)
            ]
            ws.append(row)
            wb.save(self.excel_path)
            
        except Exception as e:
            logger.error(f"Failed to write daily summary: {e}")
    
    def analyze_what_worked(self) -> List[Dict[str, Any]]:
        """Analyze successful patterns."""
        successes = []
        
        # Analyze by confidence level
        high_conf = [t for t in self.trades if t.confidence == 'high' and t.success]
        if high_conf:
            avg_profit = sum(t.net_profit for t in high_conf) / len(high_conf)
            successes.append({
                'category': 'High Confidence Trades',
                'description': f'{len(high_conf)} trades with high probability scores',
                'impact': f'+${sum(t.net_profit for t in high_conf):.2f} total profit',
                'frequency': f'{len(high_conf)}/{len(self.trades)} trades',
                'recommendation': 'Continue allocating maximum to high confidence paths'
            })
        
        # Analyze by chain length
        for length in range(5, 11):
            length_trades = [t for t in self.trades if t.chain_length == length and t.success]
            if len(length_trades) >= 3:
                win_rate = len(length_trades) / len([t for t in self.trades if t.chain_length == length]) * 100
                if win_rate > 60:
                    successes.append({
                        'category': f'{length}-Currency Chains',
                        'description': f'Chains of {length} currencies performing well',
                        'impact': f'{win_rate:.1f}% win rate',
                        'frequency': f'{len(length_trades)} successful trades',
                        'recommendation': f'Prioritize {length}-length paths'
                    })
        
        # Analyze best paths
        for path_str, stats in self.success_by_path.items():
            total = stats['wins'] + stats['losses']
            if total >= 5 and stats['wins'] / total > 0.7:
                successes.append({
                    'category': 'Winning Path',
                    'description': path_str,
                    'impact': f'+${stats["profit"]:.2f} profit',
                    'frequency': f'{stats["wins"]}/{total} successful',
                    'recommendation': 'Continue using this path'
                })
        
        return successes
    
    def analyze_what_failed(self) -> List[Dict[str, Any]]:
        """Analyze failure patterns."""
        failures = []
        
        # Analyze failed trades
        failed_trades = [t for t in self.trades if not t.success]
        
        if failed_trades:
            # Group by error type
            error_types = defaultdict(list)
            for t in failed_trades:
                error_key = t.error_message or 'Unprofitable'
                error_types[error_key].append(t)
            
            for error, trades in error_types.items():
                total_loss = sum(t.net_profit for t in trades)
                failures.append({
                    'category': 'Error Type',
                    'description': error[:50],
                    'loss_amount': f'${abs(total_loss):.2f}',
                    'frequency': f'{len(trades)} occurrences',
                    'fix': 'Review error handling and path validation'
                })
        
        # Analyze low probability trades that failed
        low_conf_failed = [t for t in failed_trades if t.confidence == 'low']
        if low_conf_failed:
            failures.append({
                'category': 'Low Confidence Trades',
                'description': 'Trades with low probability that failed',
                'loss_amount': f'${abs(sum(t.net_profit for t in low_conf_failed)):.2f}',
                'frequency': f'{len(low_conf_failed)} trades',
                'fix': 'Consider increasing minimum probability threshold'
            })
        
        # Analyze slippage issues
        high_slippage = [t for t in self.trades if abs(t.slippage) > Decimal('0.5')]
        if high_slippage:
            failures.append({
                'category': 'High Slippage',
                'description': 'Trades with >0.5% slippage',
                'loss_amount': f'${sum(t.slippage for t in high_slippage):.2f} in slippage',
                'frequency': f'{len(high_slippage)} trades',
                'fix': 'Improve execution speed or reduce allocation'
            })
        
        return failures
    
    def update_analysis_sheets(self) -> None:
        """Update all analysis sheets in Excel."""
        try:
            wb = load_workbook(self.excel_path)
            
            # Update What Worked
            ws = wb['What Worked']
            for row in range(2, ws.max_row + 1):
                for col in range(1, 6):
                    ws.cell(row=row, column=col, value=None)
            
            for i, item in enumerate(self.analyze_what_worked(), 2):
                ws.cell(row=i, column=1, value=item['category'])
                ws.cell(row=i, column=2, value=item['description'])
                ws.cell(row=i, column=3, value=item['impact'])
                ws.cell(row=i, column=4, value=item['frequency'])
                ws.cell(row=i, column=5, value=item['recommendation'])
            
            # Update What Failed
            ws = wb['What Failed']
            for row in range(2, ws.max_row + 1):
                for col in range(1, 6):
                    ws.cell(row=row, column=col, value=None)
            
            for i, item in enumerate(self.analyze_what_failed(), 2):
                ws.cell(row=i, column=1, value=item['category'])
                ws.cell(row=i, column=2, value=item['description'])
                ws.cell(row=i, column=3, value=item['loss_amount'])
                ws.cell(row=i, column=4, value=item['frequency'])
                ws.cell(row=i, column=5, value=item['fix'])
            
            # Update Path Performance
            ws = wb['Path Performance']
            for row in range(2, ws.max_row + 1):
                for col in range(1, 10):
                    ws.cell(row=row, column=col, value=None)
            
            row = 2
            for path_str, stats in sorted(
                self.success_by_path.items(),
                key=lambda x: x[1]['profit'],
                reverse=True
            ):
                total = stats['wins'] + stats['losses']
                if total > 0:
                    ws.cell(row=row, column=1, value=path_str)
                    ws.cell(row=row, column=2, value=total)
                    ws.cell(row=row, column=3, value=stats['wins'])
                    ws.cell(row=row, column=4, value=stats['losses'])
                    ws.cell(row=row, column=5, value=stats['wins'] / total * 100)
                    ws.cell(row=row, column=6, value=float(stats['profit']))
                    ws.cell(row=row, column=7, value=float(stats['profit'] / total))
                    row += 1
            
            wb.save(self.excel_path)
            logger.info("Updated analysis sheets")
            
        except Exception as e:
            logger.error(f"Failed to update analysis sheets: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.trades:
            return {'total_trades': 0}
        
        wins = sum(1 for t in self.trades if t.success)
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': wins,
            'losing_trades': len(self.trades) - wins,
            'win_rate': wins / len(self.trades) * 100,
            'total_profit': float(self.total_profit),
            'total_fees': float(self.total_fees),
            'net_profit': float(self.total_profit - self.total_fees),
            'roi': float((self.current_balance - self.starting_balance) / self.starting_balance * 100) if self.starting_balance > 0 else 0,
            'avg_profit_per_trade': float(self.total_profit / len(self.trades)),
            'best_trade': float(max(t.net_profit for t in self.trades)),
            'worst_trade': float(min(t.net_profit for t in self.trades)),
            'current_balance': float(self.current_balance)
        }
    
    def export_metrics_json(self) -> None:
        """Export metrics to JSON file."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'performance': self.get_performance_summary(),
            'what_worked': self.analyze_what_worked(),
            'what_failed': self.analyze_what_failed(),
            'path_stats': {k: {'wins': v['wins'], 'losses': v['losses'], 'profit': float(v['profit'])} 
                          for k, v in self.success_by_path.items()}
        }
        
        output_file = self.metrics_path / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        logger.info(f"Exported metrics to {output_file}")
